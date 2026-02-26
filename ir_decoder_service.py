#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import ctypes
import requests
import os

app = Flask(__name__)
CORS(app)

SO_PATH = "./libirdecode_jni_1.5.2_x86_64.so"

# 设备类型映射
CATEGORY_MAP = {
    "ac": 1,      # 空调
    "tv": 2,      # 电视机
    "stb": 3,     # 广电机顶盒
    "nw": 4,      # 网络机顶盒
    "iptv": 5,    # IPTV
    "dvd": 6,     # DVD
    "fan": 7,     # 风扇
    "projector": 8,   # 投影仪
    "stereo": 9,      # 音响
    "light": 10,      # 灯
    "robot": 11,      # 扫地机器人
    "cleaner": 12,    # 空气净化器
    "dyson": 13,      # Dyson
    "camera": 14,     # 相机
    "heater": 15      # 热水器
}

# 按键映射表
KEY_MAP = {
    "tv": {
        0: "电源", 1: "静音", 2: "上", 3: "下", 4: "左", 5: "右",
        6: "确认", 7: "音量+", 8: "音量-", 9: "返回", 10: "信号源",
        11: "菜单", 12: "主页", 13: "设置",
        14: "0", 15: "1", 16: "2", 17: "3", 18: "4",
        19: "5", 20: "6", 21: "7", 22: "8", 23: "9"
    },
    "stb": {
        0: "电源", 1: "静音", 2: "上", 3: "下", 4: "左", 5: "右",
        6: "确认", 7: "音量+", 8: "音量-", 9: "返回", 10: "信号源",
        11: "菜单", 12: "上一页", 13: "下一页",
        14: "0", 15: "1", 16: "2", 17: "3", 18: "4",
        19: "5", 20: "6", 21: "7", 22: "8", 23: "9"
    },
    "ac": {
        0: "电源", 1: "模式", 2: "温度+", 3: "温度-",
        9: "风力", 10: "扫风", 11: "固定风"
    },
    "nw": {
        0: "电源", 1: "上", 2: "下", 3: "左", 4: "右",
        5: "确认", 6: "音量+", 7: "音量-", 8: "返回", 9: "菜单", 10: "主页"
    },
    "iptv": {
        0: "电源", 1: "静音", 2: "上", 3: "下", 4: "左", 5: "右",
        6: "确认", 7: "音量+", 8: "音量-", 9: "返回", 10: "信号源",
        11: "菜单", 12: "上一页", 13: "下一页"
    },
    "dvd": {
        0: "电源", 1: "上", 2: "下", 3: "左", 4: "右",
        5: "确认", 6: "音量+", 7: "音量-", 8: "播放", 9: "暂停",
        10: "弹出", 11: "回播", 12: "快进", 13: "菜单"
    },
    "fan": {
        0: "电源", 1: "上", 2: "下", 3: "左", 4: "右",
        5: "确认", 6: "风力+", 7: "风力-", 8: "摇头",
        9: "风力", 10: "风类", 11: "返回", 12: "主页", 13: "菜单"
    },
    "projector": {
        0: "电源", 1: "上", 2: "下", 3: "左", 4: "右",
        5: "确认", 6: "音量+", 7: "音量-", 8: "缩小",
        9: "菜单", 10: "放大", 11: "返回", 12: "主页", 13: "菜单"
    },
    "stereo": {
        0: "电源", 1: "上", 2: "下", 3: "左", 4: "右",
        5: "确认", 6: "音量+", 7: "音量-", 8: "静音",
        9: "菜单", 10: "电源2", 11: "返回", 12: "主页", 13: "菜单2"
    },
    "light": {
        0: "电源", 1: "色彩1", 2: "色彩2", 3: "色彩3", 4: "色彩4",
        5: "色彩0", 6: "亮度+", 7: "亮度-", 8: "开", 9: "流光",
        10: "关", 11: "返回", 12: "主页", 13: "菜单"
    },
    "robot": {
        0: "电源", 1: "前", 2: "后", 3: "左", 4: "右",
        5: "起/停", 6: "+", 7: "-", 8: "自动", 9: "定点",
        10: "速度", 11: "定时", 12: "回充", 13: "预约"
    },
    "cleaner": {
        0: "电源", 1: "上", 2: "下", 3: "左", 4: "右",
        5: "离子", 6: "+", 7: "-", 8: "自动", 9: "风力",
        10: "模式", 11: "定时", 12: "灯光", 13: "强力"
    },
    "dyson": {
        0: "电源", 1: "风力+", 2: "风力-", 3: "定时-", 4: "定时+",
        5: "自动", 6: "温度+", 7: "温度-", 8: "摇头", 9: "扩散",
        10: "偏好", 11: "定时", 12: "睡眠", 13: "制冷"
    },
    "camera": {
        0: "电源", 1: "上", 2: "下", 3: "左", 4: "右",
        5: "拍摄", 6: "焦距+", 7: "焦距-", 8: "照相", 9: "录像",
        10: "定时", 11: "闪光", 12: "微距", 13: "夜景"
    },
    "heater": {
        0: "电源", 1: "温度+", 2: "温度-", 3: "定时-", 4: "定时+",
        5: "自动", 6: "容积+", 7: "容积-", 8: "增容", 9: "保温",
        10: "定时", 11: "节能", 12: "变频", 13: "数显"
    }
}

# 空调状态结构体
class ACStatus(ctypes.Structure):
    _fields_ = [
        ("ac_power", ctypes.c_uint8),      # 0=开, 1=关
        ("ac_mode", ctypes.c_uint8),       # 0=制冷,1=制热,2=自动,3=送风,4=除湿
        ("ac_temp", ctypes.c_uint8),       # 0-14 (16-30度)
        ("ac_wind_speed", ctypes.c_uint8), # 0=自动,1=弱,2=中,3=强
        ("ac_wind_dir", ctypes.c_uint8),   # 0=摆风,1=固定
        ("change_wind_direction", ctypes.c_uint8)  # 0/1
    ]

class IRDecoder:
    def __init__(self, so_path):
        self.lib = ctypes.CDLL(so_path)
        self.lib.get_lib_version.restype = ctypes.c_char_p
        
        # ir_binary_open(category, sub_category, binary, binary_length)
        self.lib.ir_binary_open.argtypes = [
            ctypes.c_uint8, 
            ctypes.c_uint8, 
            ctypes.POINTER(ctypes.c_ubyte), 
            ctypes.c_uint16
        ]
        self.lib.ir_binary_open.restype = ctypes.c_int8
        
        # ir_decode(key_code, user_data, ac_status)
        self.lib.ir_decode.argtypes = [
            ctypes.c_uint8, 
            ctypes.POINTER(ctypes.c_uint16), 
            ctypes.c_void_p
        ]
        self.lib.ir_decode.restype = ctypes.c_uint16
        
        # ir_close()
        self.lib.ir_close.argtypes = []
        self.lib.ir_close.restype = ctypes.c_int8
        
        # get_supported_mode
        self.lib.get_supported_mode.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        self.lib.get_supported_mode.restype = ctypes.c_int8
        
        # get_temperature_range
        self.lib.get_temperature_range.argtypes = [
            ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_int8),
            ctypes.POINTER(ctypes.c_int8)
        ]
        self.lib.get_temperature_range.restype = ctypes.c_int8
        
        # get_supported_wind_speed
        self.lib.get_supported_wind_speed.argtypes = [
            ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.get_supported_wind_speed.restype = ctypes.c_int8
        
    def get_version(self):
        return self.lib.get_lib_version().decode('utf-8')
    
    def decode(self, bin_data, key_code, category=2, sub_category=1):
        """解码单个按键（TV/机顶盒等）"""
        arr = (ctypes.c_ubyte * len(bin_data))(*bin_data)
        
        ret = self.lib.ir_binary_open(category, sub_category, arr, len(bin_data))
        if ret != 0:
            return {"error": f"ir_binary_open failed: {ret}"}
        
        timings = (ctypes.c_uint16 * 1024)()
        count = self.lib.ir_decode(key_code, timings, None)
        
        self.lib.ir_close()
        
        return {
            "timings": list(timings[:count]),
            "count": count
        }
    
    def decode_all(self, bin_data, category=2, sub_category=1):
        """解码所有按键（TV/机顶盒等）"""
        arr = (ctypes.c_ubyte * len(bin_data))(*bin_data)
        
        ret = self.lib.ir_binary_open(category, sub_category, arr, len(bin_data))
        if ret != 0:
            return {"error": f"ir_binary_open failed: {ret}"}
        
        results = {}
        for idx in range(256):
            timings = (ctypes.c_uint16 * 1024)()
            count = self.lib.ir_decode(idx, timings, None)
            if count == 0:
                continue
            results[idx] = {
                "count": count,
                "timings": list(timings[:count])
            }
        
        self.lib.ir_close()
        return {"keys": results, "total": len(results)}
    
    def decode_ac(self, bin_data, ac_status_dict, category=1, sub_category=1):
        """解码空调 - 使用ir_decode"""
        arr = (ctypes.c_ubyte * len(bin_data))(*bin_data)
        
        ret = self.lib.ir_binary_open(category, sub_category, arr, len(bin_data))
        if ret != 0:
            return {"error": f"ir_binary_open failed: {ret}"}
        
        # 构造ACStatus
        ac_status = ACStatus()
        ac_status.ac_power = ac_status_dict.get("acPower", 0)
        ac_status.ac_mode = ac_status_dict.get("acMode", 0)
        ac_status.ac_temp = ac_status_dict.get("acTemp", 8)
        ac_status.ac_wind_speed = ac_status_dict.get("acWindSpeed", 0)
        ac_status.ac_wind_dir = ac_status_dict.get("acWindDir", 0)
        ac_status.change_wind_direction = ac_status_dict.get("changeWindDir", 0)
        
        timings = (ctypes.c_uint16 * 1024)()
        
        # 使用ir_decode，传入ac_status作为第三个参数
        key_code = ac_status_dict.get("keyCode", 0)
        count = self.lib.ir_decode(key_code, timings, ctypes.byref(ac_status))
        
        self.lib.ir_close()
        
        return {
            "timings": list(timings[:count]),
            "count": count,
            "acStatus": {
                "acPower": ac_status.ac_power,
                "acMode": ac_status.ac_mode,
                "acTemp": ac_status.ac_temp,
                "acWindSpeed": ac_status.ac_wind_speed,
                "acWindDir": ac_status.ac_wind_dir,
                "changeWindDir": ac_status.change_wind_direction
            }
        }
    
    def get_ac_parameters(self, bin_data, mode, category=1, sub_category=1):
        """获取空调支持的参数"""
        arr = (ctypes.c_ubyte * len(bin_data))(*bin_data)
        
        ret = self.lib.ir_binary_open(category, sub_category, arr, len(bin_data))
        if ret != 0:
            return {"error": f"ir_binary_open failed: {ret}"}
        
        # 支持的模式
        supported_modes = ctypes.c_uint8()
        self.lib.get_supported_mode(ctypes.byref(supported_modes))
        
        # 温度范围
        temp_min = ctypes.c_int8()
        temp_max = ctypes.c_int8()
        self.lib.get_temperature_range(mode, ctypes.byref(temp_min), ctypes.byref(temp_max))
        
        # 风力档
        supported_wind_speed = ctypes.c_uint8()
        self.lib.get_supported_wind_speed(mode, ctypes.byref(supported_wind_speed))
        
        self.lib.ir_close()
        
        return {
            "supportedModes": supported_modes.value,
            "tempMin": temp_min.value,
            "tempMax": temp_max.value,
            "supportedWindSpeed": supported_wind_speed.value
        }

decoder = IRDecoder(SO_PATH)

def get_category_id(device_type):
    """获取设备类型ID"""
    return CATEGORY_MAP.get(device_type.lower(), 2)

def get_key_name(device_type, index):
    """根据索引获取按键名称"""
    device_type = device_type.lower() if device_type else "tv"
    key_map = KEY_MAP.get(device_type, KEY_MAP["tv"])
    return key_map.get(index, f"按键{index}")

@app.route('/keys', methods=['GET'])
def list_keys():
    """获取所有支持的按键映射"""
    return jsonify({
        "status": 0,
        "categories": CATEGORY_MAP,
        "keyMap": KEY_MAP
    })

@app.route('/decode', methods=['POST'])
def decode():
    """解码单个按键"""
    try:
        data = request.get_json()
        id_val = data.get("id")
        token = data.get("token")
        index_id = data.get("indexId")
        device_type = data.get("deviceType", "tv")
        key_input = data.get("key", "0")
        category_id = data.get("categoryId")
        sub_cate = data.get("subCate")
        # 原版 URL：srv.irext.net
        irext_url = data.get("irextUrl", "https://srv.irext.net/irext-server/operation/download_bin")
        
        if not all([id_val, token, index_id]):
            return jsonify({"error": "缺少必要参数: id, token, indexId"}), 400
        
        if category_id is None:
            category_id = get_category_id(device_type)
        else:
            category_id = int(category_id)
        
        if sub_cate is None:
            sub_cate = 1
        else:
            sub_cate = int(sub_cate)
        
        # 空调用特殊接口
        if category_id == 1 or device_type.lower() == "ac":
            return jsonify({"error": "空调请使用 /ac/decode 接口"}), 400
        
        try:
            key_index = int(key_input)
        except (ValueError, TypeError):
            device_type = device_type.lower()
            key_map = KEY_MAP.get(device_type, {})
            key_index = None
            for idx, name in key_map.items():
                if name == key_input:
                    key_index = idx
                    break
            if key_index is None:
                return jsonify({"error": f"未知的按键名称: {key_input}"}), 400
        
        resp = requests.post(irext_url, json={
            "id": str(id_val),
            "token": token,
            "indexId": str(index_id)
        }, timeout=30)
        
        if resp.status_code != 200:
            return jsonify({"error": f"下载失败: HTTP {resp.status_code}", "detail": resp.text}), 502
        
        bin_data = resp.content
        
        if len(bin_data) < 500:
            try:
                err_json = resp.json()
                if "status" in err_json and err_json.get("status", {}).get("code", 0) != 0:
                    return jsonify({"error": "IRext 返回错误", "detail": err_json}), 502
            except:
                pass
        
        result = decoder.decode(bin_data, key_index, category_id, sub_cate)
        
        if "error" in result:
            return jsonify({"status": -1, "error": result["error"]}), 500
        
        key_name = get_key_name(device_type, key_index)
        
        return jsonify({
            "status": 0,
            "indexId": index_id,
            "deviceType": device_type,
            "categoryId": category_id,
            "subCate": sub_cate,
            "key": key_name,
            "keyIndex": key_index,
            "binSize": len(bin_data),
            "timings": result["timings"],
            "count": result["count"]
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "无法连接到 IRext 服务"}), 503
    except Exception as e:
        return jsonify({"status": -1, "error": str(e)}), 500

@app.route('/decode/all', methods=['POST'])
def decode_all():
    """解码所有按键"""
    try:
        data = request.get_json()
        id_val = data.get("id")
        token = data.get("token")
        index_id = data.get("indexId")
        device_type = data.get("deviceType", "tv")
        category_id = data.get("categoryId")
        sub_cate = data.get("subCate")
        # 原版 URL：srv.irext.net
        irext_url = data.get("irextUrl", "https://srv.irext.net/irext-server/operation/download_bin")
        
        if not all([id_val, token, index_id]):
            return jsonify({"error": "缺少必要参数"}), 400
        
        if category_id is None:
            category_id = get_category_id(device_type)
        else:
            category_id = int(category_id)
        
        if sub_cate is None:
            sub_cate = 1
        else:
            sub_cate = int(sub_cate)
        
        # 空调用特殊接口
        if category_id == 1 or device_type.lower() == "ac":
            return jsonify({"error": "空调请使用 /ac/decode 接口"}), 400
        
        resp = requests.post(irext_url, json={
            "id": str(id_val),
            "token": token,
            "indexId": str(index_id)
        }, timeout=30)
        
        if resp.status_code != 200:
            return jsonify({"error": f"下载失败: HTTP {resp.status_code}"}), 502
        
        bin_data = resp.content
        
        result = decoder.decode_all(bin_data, category_id, sub_cate)
        
        if "error" in result:
            return jsonify({"status": -1, "error": result["error"]}), 500
        
        keys_with_name = {}
        for idx, val in result["keys"].items():
            key_name = get_key_name(device_type, idx)
            keys_with_name[key_name] = {
                "index": idx,
                **val
            }
        
        return jsonify({
            "status": 0,
            "indexId": index_id,
            "deviceType": device_type,
            "categoryId": category_id,
            "subCate": sub_cate,
            "totalKeys": result["total"],
            "keys": keys_with_name
        })
        
    except Exception as e:
        return jsonify({"status": -1, "error": str(e)}), 500

@app.route('/ac/decode', methods=['POST'])
def ac_decode():
    """空调解码"""
    try:
        data = request.get_json()
        id_val = data.get("id")
        token = data.get("token")
        index_id = data.get("indexId")
        category_id = data.get("categoryId", 1)
        sub_cate = data.get("subCate")
        # 原版 URL：srv.irext.net
        irext_url = data.get("irextUrl", "https://srv.irext.net/irext-server/operation/download_bin")
        
        # ACStatus 参数
        ac_status_dict = {
            "acPower": data.get("acPower", 0),
            "acMode": data.get("acMode", 0),
            "acTemp": data.get("acTemp", 8),
            "acWindSpeed": data.get("acWindSpeed", 0),
            "acWindDir": data.get("acWindDir", 0),
            "changeWindDir": data.get("changeWindDir", 0),
            "keyCode": data.get("keyCode", 0)
        }
        
        if not all([id_val, token, index_id]):
            return jsonify({"error": "缺少必要参数: id, token, indexId"}), 400
        
        if sub_cate is None:
            sub_cate = 1
        else:
            sub_cate = int(sub_cate)
        
        resp = requests.post(irext_url, json={
            "id": str(id_val),
            "token": token,
            "indexId": str(index_id)
        }, timeout=30)
        
        if resp.status_code != 200:
            return jsonify({"error": f"下载失败: HTTP {resp.status_code}", "detail": resp.text}), 502
        
        bin_data = resp.content
        
        if len(bin_data) < 500:
            try:
                err_json = resp.json()
                if "status" in err_json and err_json.get("status", {}).get("code", 0) != 0:
                    return jsonify({"error": "IRext 返回错误", "detail": err_json}), 502
            except:
                pass
        
        result = decoder.decode_ac(bin_data, ac_status_dict, category_id, sub_cate)
        
        if "error" in result:
            return jsonify({"status": -1, "error": result["error"]}), 500
        
        return jsonify({
            "status": 0,
            "indexId": index_id,
            "deviceType": "ac",
            "categoryId": category_id,
            "subCate": sub_cate,
            "binSize": len(bin_data),
            "acStatus": result["acStatus"],
            "timings": result["timings"],
            "count": result["count"]
        })
        
    except Exception as e:
        return jsonify({"status": -1, "error": str(e)}), 500

@app.route('/ac/parameters', methods=['POST'])
def ac_parameters():
    """获取空调支持的参数"""
    try:
        data = request.get_json()
        id_val = data.get("id")
        token = data.get("token")
        index_id = data.get("indexId")
        mode = data.get("mode", 0)
        category_id = data.get("categoryId", 1)
        sub_cate = data.get("subCate")
        # 原版 URL：srv.irext.net
        irext_url = data.get("irextUrl", "https://srv.irext.net/irext-server/operation/download_bin")
        
        if not all([id_val, token, index_id]):
            return jsonify({"error": "缺少必要参数"}), 400
        
        if sub_cate is None:
            sub_cate = 1
        else:
            sub_cate = int(sub_cate)
        
        resp = requests.post(irext_url, json={
            "id": str(id_val),
            "token": token,
            "indexId": str(index_id)
        }, timeout=30)
        
        if resp.status_code != 200:
            return jsonify({"error": f"下载失败: HTTP {resp.status_code}"}), 502
        
        bin_data = resp.content
        
        result = decoder.get_ac_parameters(bin_data, mode, category_id, sub_cate)
        
        if "error" in result:
            return jsonify({"status": -1, "error": result["error"]}), 500
        
        return jsonify({
            "status": 0,
            "indexId": index_id,
            "mode": mode,
            "parameters": result
        })
        
    except Exception as e:
        return jsonify({"status": -1, "error": str(e)}), 500

@app.route('/decode/local', methods=['POST'])
def decode_local():
    """解码本地 bin 文件"""
    try:
        data = request.get_json()
        bin_path = data.get("binPath")
        device_type = data.get("deviceType", "tv")
        category_id = data.get("categoryId")
        sub_cate = data.get("subCate")
        
        if not bin_path or not os.path.exists(bin_path):
            return jsonify({"error": f"文件不存在: {bin_path}"}), 400
        
        if category_id is None:
            category_id = get_category_id(device_type)
        else:
            category_id = int(category_id)
        
        if sub_cate is None:
            sub_cate = 1
        else:
            sub_cate = int(sub_cate)
        
        with open(bin_path, 'rb') as f:
            bin_data = f.read()
        
        # 空调用特殊接口
        if category_id == 1 or device_type.lower() == "ac":
            return jsonify({"error": "空调请使用 /ac/decode/local 接口"}), 400
        
        result = decoder.decode_all(bin_data, category_id, sub_cate)
        
        if "error" in result:
            return jsonify({"status": -1, "error": result["error"]}), 500
        
        keys_with_name = {}
        for idx, val in result["keys"].items():
            key_name = get_key_name(device_type, idx)
            keys_with_name[key_name] = {
                "index": idx,
                **val
            }
        
        return jsonify({
            "status": 0,
            "binPath": bin_path,
            "deviceType": device_type,
            "categoryId": category_id,
            "subCate": sub_cate,
            "totalKeys": result["total"],
            "keys": keys_with_name
        })
    except Exception as e:
        return jsonify({"status": -1, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "decoder_version": decoder.get_version()
    })

if __name__ == '__main__':
    print(f"IR Decoder Service")
    print(f"Version: {decoder.get_version()}")
    print(f"Listening on http://0.0.0.0:8082 ")
    app.run(host='0.0.0.0', port=8082, threaded=True)
