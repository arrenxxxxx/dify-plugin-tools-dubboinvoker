# -*- coding: utf-8 -*-
"""
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""

"""
把Python的数据结构根据Hessian协议序列化为相应的字节数组
当前支持的数据类型：
* bool
* int
* long
* float
* double
* java.lang.String
* java.lang.Object
"""
import struct
import re
from typing import Any, Dict, List, Optional, Union

from dubbo.common.constants import MIN_INT_32, MAX_INT_32, DEFAULT_REQUEST_META
from dubbo.common.exceptions import HessianTypeError
from dubbo.common.util import double_to_long_bits, get_invoke_id

# 支持的基础类型映射
BASIC_TYPE_MAPPING = {
    'boolean': 'Z',
    'bool': 'Z',
    'int': 'I',
    'integer': 'I',
    'long': 'J',
    'float': 'F',
    'double': 'D',
    'byte': 'B',
    'char': 'C',
    'short': 'S',
    'void': 'V'
}

class Object(object):
    """
    对应Java的实体对象
    """

    def __init__(self, path, values=None):
        """
        :param path: Java对象的路径，例如：java.lang.Object
        :param values: 构造函数的参数
        """
        self.__path = path  # 对象的路径全名
        self.__values = values or {}  # 对象的属性字典

    def get_path(self):
        return self.__path

    def __getitem__(self, key):
        return self.__values.get(key)

    def __setitem__(self, key, value):
        self.__values[key] = value

    def __iter__(self):
        return iter(self.__values)

    def __str__(self):
        return f"{self.__path}: {str(self.__values)}"

    __repr__ = __str__


class Request(object):
    """
    请求对象
    """

    def __init__(self, request_param):
        # 初始化请求参数
        self.request_param = request_param
        self.dubbo_version = request_param.get('dubbo_version', '2.4.10')
        self.service_name = request_param.get('path')
        self.service_version = request_param.get('version', '')
        self.method = request_param.get('method')
        self.arguments = request_param.get('arguments', [])
        self.parameter_types = request_param.get('parameter_types', None)
        self.attachments = request_param.get('attachments', {})
        self.invoke_id = request_param.get('invoke_id', None) or get_invoke_id()
        self.types = []  # 泛型类型列表，用于编码列表

    def encode(self):
        """
        把请求参数转化为字节数组
        :return:
        """
        request_body = self._encode_request_body()
        request_head = self._build_request_head(len(request_body))
        return bytearray(request_head + request_body)

    def _build_request_head(self, body_len):
        """
        构建请求头
        :param body_len:
        :return:
        """
        # 使用默认的请求头
        head = list(DEFAULT_REQUEST_META)
        # 写入invoke_id
        head[4:12] = list(struct.pack('!q', self.invoke_id))
        # 写入body长度
        head[12:] = list(struct.pack('!i', body_len))
        return head

    def _encode_request_body(self):
        """
        构建请求体
        :return:
        """
        result = []
        # 写入dubbo版本号
        result.extend(self._encode_single_value(self.dubbo_version))
        # 写入service_path
        result.extend(self._encode_single_value(self.service_name))
        # 写入service_version
        result.extend(self._encode_single_value(self.service_version))
        # 写入方法名
        result.extend(self._encode_single_value(self.method))

        # 使用parameter_types优先处理参数类型
        if self.parameter_types:
            result.extend(self._encode_method_parameter_types())
        else:
            # 写入方法的所有参数类型，如果有则以参数类型开头
            if self.arguments:
                parameter_types = ','.join([self._get_class_name(argument) for argument in self.arguments])
                result.extend(self._encode_single_value(parameter_types))
            else:
                result.extend(self._encode_single_value(''))

        # 写入方法的所有参数值
        for argument in self.arguments:
            result.extend(self._encode_single_value(argument))

        # 写入隐藏传参
        result.extend(self._encode_attachments())

        return result

    def _encode_method_parameter_types(self):
        """
        编码方法参数类型列表
        :return:
        """
        # 转换参数类型到Java描述符格式
        java_desc_list = []
        for param_type in self.parameter_types:
            if param_type.lower() in BASIC_TYPE_MAPPING:
                # 处理基础类型
                java_desc_list.append(BASIC_TYPE_MAPPING[param_type.lower()])
            elif param_type.endswith('[]'):
                # 处理数组类型
                base_type = param_type[:-2]
                if base_type.lower() in BASIC_TYPE_MAPPING:
                    # 基础类型数组
                    java_desc_list.append('[' + BASIC_TYPE_MAPPING[base_type.lower()])
                else:
                    # 对象类型数组
                    java_desc_list.append('[L' + base_type.replace('.', '/') + ';')
            else:
                # 处理对象类型
                java_desc_list.append('L' + param_type.replace('.', '/') + ';')
        
        # 将Java描述符格式的类型合并为一个字符串
        parameter_types_str = ''.join(java_desc_list)
        return self._encode_single_value(parameter_types_str)

    def _get_class_name(self, _class):
        """
        根据一个字段的类型得到其在Java中对应类的全限定名
        转换规则：https://stackoverflow.com/a/3442100/4614538
        :param _class:
        :return:
        """
        if isinstance(_class, bool):  # bool类型的判断必须放在int类型判断的前面
            return 'Z'
        elif isinstance(_class, int):
            if MIN_INT_32 <= _class <= MAX_INT_32:
                return 'I'
            else:
                return 'J'
        elif isinstance(_class, float):
            return 'D'
        elif isinstance(_class, str):
            return 'L' + 'java/lang/String' + ';'
        elif isinstance(_class, Object):
            path = _class.get_path()
            path = 'L' + path.replace('.', '/') + ';'
            return path
        elif isinstance(_class, list):
            if len(_class) == 0:
                raise HessianTypeError('Method parameter {} is a list but length is zero'.format(_class))
            return '[' + self._get_class_name(_class[0])
        else:
            raise HessianTypeError('Unknown argument type: {0}'.format(_class))

    def _encode_attachments(self):
        """
        编码隐藏参数
        :return:
        """
        attachments = self.attachments
        result = []
        if not attachments:
            result.append(ord('H'))
            result.append(ord('Z'))
            return result

        # 以H开头
        result.append(ord('H'))
        for key in attachments:
            result.extend(self._encode_single_value(key))
            result.extend(self._encode_single_value(attachments[key]))
        # 最后以Z结束
        result.append(ord('Z'))
        return result

    def _encode_list(self, value):
        """
        对一个列表进行编码
        :param value:
        :return:
        """
        result = []
        length = len(value)
        if length == 0:
            # 没有值则无法判断类型，一律返回null
            return self._encode_single_value(None)
        if isinstance(value[0], bool):
            _type = '[boolean'
        elif isinstance(value[0], int):
            _type = '[int'
        elif isinstance(value[0], float):
            _type = '[double'
        elif isinstance(value[0], str):
            _type = '[string'
        elif isinstance(value[0], Object):
            _type = '[object'
        else:
            raise HessianTypeError('Unknown list type: {}'.format(value[0]))
        if length < 0x7:
            result.append(0x70 + length)
            if _type not in self.types:
                self.types.append(_type)
                result.extend(self._encode_single_value(_type))
            else:
                result.extend(self._encode_single_value(self.types.index(_type)))
        else:
            result.append(0x56)
            if _type not in self.types:
                self.types.append(_type)
                result.extend(self._encode_single_value(_type))
            else:
                result.extend(self._encode_single_value(self.types.index(_type)))
            result.extend(self._encode_single_value(length))
        for v in value:
            if type(value[0]) != type(v):
                raise HessianTypeError('All elements in list must be the same type, first type'
                                       ' is {0} but current type is {1}'.format(type(value[0]), type(v)))
            result.extend(self._encode_single_value(v))
        return result

    def _encode_single_value(self, value):
        """
        根据hessian协议对单个变量进行编码
        :param value:
        :return:
        """
        # 布尔类型
        if isinstance(value, bool):
            return self._encode_bool(value)
        # 整型（包括长整型）
        elif isinstance(value, int):
            return self._encode_int(value)
        # 浮点类型
        elif isinstance(value, float):
            return self._encode_float(value)
        # 字符串类型
        elif isinstance(value, str):
            return self._encode_str(value)
        # 对象类型
        elif isinstance(value, Object):
            return self._encode_object(value)
        # 列表(list)类型，不可以使用tuple替代
        elif isinstance(value, list):
            return self._encode_list(value)
        # null
        elif value is None:
            return [ord('N')]
        else:
            raise HessianTypeError('Unknown argument type: {}'.format(value))

    def _encode_bool(self, value):
        return [ord('T')] if value else [ord('F')]

    def _encode_int(self, value):
        if MIN_INT_32 <= value <= MAX_INT_32:
            # 超出了4个字节的范围，使用8个字节的long类型进行编码
            if -0x10 <= value <= 0x2f:
                return [0x90 + value]
            elif -0x800 <= value <= 0x7ff:
                result = [0xc8 + (value >> 8)]
                result.append(value & 0xff)
                return result
            elif -0x40000 <= value <= 0x3ffff:
                result = [0xd4 + (value >> 16)]
                result.append((value >> 8) & 0xff)
                result.append(value & 0xff)
                return result
            else:
                return [ord('I')] + list(struct.pack('!i', value))
        else:
            # 数字如果大于int_32的范围则将之按照long类型进行编码
            return self._encode_long(value)

    def _encode_long(self, value):
        if -0x08 <= value <= 0x0f:
            return [0xe0 + value]
        elif -0x800 <= value <= 0x7ff:
            result = [0xf8 + (value >> 8)]
            result.append(value & 0xff)
            return result
        elif -0x40000 <= value <= 0x3ffff:
            result = [0x3c + (value >> 16)]
            result.append((value >> 8) & 0xff)
            result.append(value & 0xff)
            return result
        elif -0x80000000 <= value <= 0x7fffffff:
            return [0x59] + list(struct.pack('!i', value))
        else:
            return [ord('L')] + list(struct.pack('!q', value))

    def _encode_float(self, value):
        if value == 0.0:
            return [0x5b]
        elif value == 1.0:
            return [0x5c]
        elif int(value) == value and -0x80 <= value <= 0x7f:
            return [0x5d] + list(struct.pack('!b', int(value)))
        elif int(value) == value and -0x8000 <= value <= 0x7fff:
            return [0x5e] + list(struct.pack('!h', int(value)))
        else:
            bits = double_to_long_bits(value)
            return [ord('D')] + list(struct.pack('!d', value))

    def _encode_str(self, value):
        value = value.encode('utf-8')
        length = len(value)
        if length <= 0x1f:
            return [0x00 + length] + list(value)
        else:
            result = []
            # 把字符串分成多段，每段最多65535个字符
            for i in range(int(length / 0xffff) + 1):
                current_length = min(0xffff, length - 0xffff * i)
                if i == int(length / 0xffff):
                    # 最后一个分块
                    result = result + [0x53, (current_length >> 8) & 0xff, current_length & 0xff] + \
                                        list(value[0xffff * i:0xffff * i + current_length])
                else:
                    # 当前不是最后一个分块
                    result = result + [0x52, (current_length >> 8) & 0xff, current_length & 0xff] + \
                                        list(value[0xffff * i:0xffff * i + current_length])
            return result

    def _encode_object(self, value):
        """
        TODO: 这里暂时无法实现，因为需要把Python的基本类型映射到Java对象上
        参考: https://github.com/apache/dubbo-python/blob/master/dubbo/serialization/hessian2.py#L243
        :param value:
        :return:
        """
        # path = value.get_path()
        # field_names = []
        # field_values = []
        # for field_name in value:
        #     field_names.append(field_name)
        #     field_values.append(value[field_name])
        # result = []
        # result.append(ord('M'))
        # result.extend(self._encode_single_value(path))
        # keys = list(field_names)
        # for i in range(len(keys)):
        #     key = keys[i]
        #     value = field_values[i]
        #     result.extend(self._encode_single_value(str(key)))
        #     result.extend(self._encode_single_value(value))
        # result.append(ord('Z'))
        # return result
        raise HessianTypeError('Not implemented: object serialization')

def encode_request(request_param):
    req = Request(request_param)
    return req.encode()


def has_chinese(msg: str):
    result = re.compile('[\u4e00-\u9fff]+').findall(msg)
    return len(result) > 0


def get_request_body_length(body):
    """
    获取body的长度，并将其转为长度为4个字节的字节数组
    :param body:
    :return:
    """
    return list(bytearray(struct.pack('!i', len(body))))


if __name__ == '__main__':
    pass
