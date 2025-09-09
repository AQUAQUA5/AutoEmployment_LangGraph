# VPN/VM 탐지 우회용 프로필
USER_PROFILE = {
    # 기존 설정 그대로 유지
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "viewport": {"width": 864, "height": 1536},
    "locale": "ko-KR",
    "timezone_id": "Asia/Seoul",
    
    # 지리적 위치 (서울 관악구)
    "geolocation": {
        "latitude": 37.4873, 
        "longitude": 126.9227
    },
    
    # HTTP 헤더 설정
    "extra_http_headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": '"Google Chrome";v="139", "Chromium";v="139", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    },
    
    # 하드웨어 정보 (실제 시스템 스펙)
    "hardware_concurrency": 16,
    "device_memory": 8,
    "platform": "Win32",
    "max_touch_points": 10,
    "color_depth": 24,
    
    # 언어 및 지역 설정
    "languages": ["ko-KR"],
    "cookie_enabled": True,
    
    # WebGL 정보 (AMD 그래픽스)
    "webgl_vendor": "Google Inc. (AMD)",
    "webgl_renderer": "ANGLE (AMD, AMD Radeon(TM) Graphics (0x00001900) Direct3D11 vs_5_0 ps_5_0, D3D11)",
    
    # 화면 정보
    "screen_resolution": [864, 1536],
    "screen_frame": [0, 0, 50, 0],
    
    # 디바이스 특성
    "is_mobile": False,
    "has_touch": False,
    "device_scale_factor": 1,
    "permissions": ["geolocation"],
    
    # 추가 브라우저 특성
    "pdf_viewer_enabled": True,
    "session_storage": True,
    "local_storage": True,
    "indexed_db": True,
    "reduced_motion": False,
    "forced_colors": False,
    "color_gamut": "srgb",
    "monochrome": 0,
    "contrast": 0,
    "inverted_colors": False
}

# VM 탐지 우회를 위한 브라우저 실행 옵션
BROWSER_ARGS = [
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-blink-features=AutomationControlled',
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--enable-webgl',
    '--enable-accelerated-2d-canvas',
    '--memory-pressure-off',
    
    # VM 탐지 우회 관련
    '--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    
    # 실제 하드웨어처럼 보이게
    '--enable-gpu-rasterization',
    '--enable-zero-copy',
    '--enable-features=VaapiVideoDecoder',
    '--use-gl=desktop',
]

# maxTouchPoints와 Client Hints 문제 해결을 위한 수정된 스크립트
def get_fingerprint_script():
    return f"""
        // 1. WebDriver 제거 (기본)
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined
        }});
        delete navigator.__proto__.webdriver;
        delete navigator.webdriver;
        
        // 2. VM 탐지 우회 - 하드웨어 가속 관련
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {USER_PROFILE['hardware_concurrency']}
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {USER_PROFILE['device_memory']}
        }});
        
        // 3. maxTouchPoints 수정 (가장 중요!)
        Object.defineProperty(navigator, 'maxTouchPoints', {{
            get: () => {USER_PROFILE['max_touch_points']},
            configurable: true
        }});
        
        // 4. WebGL 렌더러 정보 (VM이 아닌 실제 하드웨어처럼)
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{USER_PROFILE['webgl_vendor']}';
            }}
            if (parameter === 37446) {{
                return '{USER_PROFILE['webgl_renderer']}';
            }}
            return getParameter.call(this, parameter);
        }};
        
        // 5. 플랫폼 정보 정확히 설정
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{USER_PROFILE['platform']}'
        }});
        
        // 6. Client Hints 버전 일치 (Chrome 140)
        if (navigator.userAgentData) {{
            Object.defineProperty(navigator.userAgentData, 'brands', {{
                get: () => [
                    {{"brand": "Chromium", "version": "140"}},
                    {{"brand": "Not=A?Brand", "version": "24"}},
                    {{"brand": "Google Chrome", "version": "140"}}
                ]
            }});
            
            Object.defineProperty(navigator.userAgentData, 'fullVersionList', {{
                get: () => [
                    {{"brand": "Chromium", "version": "140.0.7339.80"}},
                    {{"brand": "Not=A?Brand", "version": "24.0.0.0"}},
                    {{"brand": "Google Chrome", "version": "140.0.7339.80"}}
                ]
            }});
            
            Object.defineProperty(navigator.userAgentData, 'uaFullVersion', {{
                get: () => "140.0.7339.80"
            }});
        }}
        
        // 7. 자동화 도구 흔적 제거
        ['__webdriver_evaluate', '__selenium_evaluate', '__webdriver_script_function', '__webdriver_script_func', '__webdriver_script_fn', '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped', '__driver_evaluate', '__selenium_unwrapped', '__fxdriver_unwrapped'].forEach(prop => {{
            Object.defineProperty(window, prop, {{
                get: () => undefined
            }});
        }});
        
        // 8. Chrome 객체 기본 설정
        if (!window.chrome) {{
            window.chrome = {{
                runtime: {{}}
            }};
        }}
        
        // 완료
    """