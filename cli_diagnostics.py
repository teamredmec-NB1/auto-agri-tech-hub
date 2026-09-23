#!/usr/bin/env python3
# coding: utf-8
"""
Diesel Engine CLI Diagnostic & Engineering Calculator Utility
Tool for searching troubleshooting guides, DTC codes, and calculating engine metrics.
"""

import sys
import argparse
import math

TROUBLESHOOT_DB = [
    {
        "id": "FT-01", "category": "สีควันไอเสีย", "symptom": "ควันดำหนาแน่นขณะเร่งโหลด (Dense Black Smoke)",
        "cause": "มวลอากาศไม่พอกับปริมาณน้ำมัน (Rich Mixture) อัตราส่วน Lambda < 1.15",
        "system": "ระบบประจุไอดี / เทอร์โบชาร์จเจอร์",
        "diagnostic": "1. วัดแรงดันบูสต์เทอร์โบ 2. ตรวจเกจวัดกรองอากาศ 3. สโมกเทสต์หารอยรั่วท่ออินเตอร์",
        "action": "เปลี่ยนไส้กรองอากาศ, ซ่อมท่ออินเตอร์คูลเลอร์ที่แตก, ปรับตั้งเวสต์เกต"
    },
    {
        "id": "FT-02", "category": "สีควันไอเสีย", "symptom": "ควันดำตลอดเวลาแม้เดินเบา (Continuous Black Smoke at Idle)",
        "cause": "หัวฉีดจ่ายน้ำมันรั่วซึม ปลายหัวฉีดสึกหรอ ฉีดเป็นหยดไม่เป็นฝอย",
        "system": "ระบบเชื้อเพลิงคอมมอนเรล",
        "diagnostic": "1. ดูค่า Injector Balance Rates ด้วยเครื่องสแกน 2. ทำ Back Leak Test",
        "action": "ถอดหัวฉีดส่งเช็กปั๊ม-หัวฉีด เปลี่ยนชุดปลายเข็มและวาล์วคอนโทรล"
    },
    {
        "id": "FT-03", "category": "สีควันไอเสีย", "symptom": "ควันขาวฟุ้งตอนสตาร์ทช่วงเช้า (White Smoke on Cold Start)",
        "cause": "อุณหภูมิในห้องเผาไหม้ต่ำเกินไป ละอองน้ำมันไม่ระเบิดแต่ระเหยออกท่อไอเสีย",
        "system": "ระบบสตาร์ท / กำลังอัด",
        "diagnostic": "1. วัดความต้านทานหัวเผา (< 1-2 Ohm) 2. วัดกำลังอัด",
        "action": "เปลี่ยนหัวเผาตัวที่ขาด หรือเปลี่ยนรีเลย์ควบคุมหัวเผา"
    },
    {
        "id": "FT-04", "category": "สีควันไอเสีย", "symptom": "ควันขาวตลอดเวลา มีกลิ่นหวาน (Continuous Sweet White Smoke)",
        "cause": "น้ำหล่อเย็นเล็ดลอดเข้าห้องเผาไหม้ ระเหยกลายเป็นไอน้ำพุ่งออกปลายท่อ",
        "system": "ระบบระบายความร้อน / ปะเก็นฝาสูบ",
        "diagnostic": "1. ตรวจระดับน้ำหล่อเย็น 2. ใช้ชุดทดสอบ Combustion Leak Test ดูก๊าซในหม้อน้ำ",
        "action": "เปิดฝาสูบ เปลี่ยนปะเก็นฝาสูบ ไสปรับระนาบฝาสูบใหม่หากโก่ง"
    },
    {
        "id": "FT-06", "category": "สีควันไอเสีย", "symptom": "ควันสีขาวอมฟ้าตลอดเวลา (Continuous Blue Smoke)",
        "cause": "น้ำมันเครื่องเล็ดลอดขึ้นจากห้องแคร้งก์เข้าสู่ห้องเผาไหม้เนื่องจากแหวนลูกสูบหัก/ตาย",
        "system": "กลไกเพลาข้อเหวี่ยงและลูกสูบ",
        "diagnostic": "1. วัดกำลังอัดแบบ Wet & Dry Compression Test 2. ส่องกล้อง Borescope",
        "action": "รื้อโอเวอร์ฮอล คว้านกระบอกสูบ ตีปลอกใหม่ เปลี่ยนลูกสูบและแหวน"
    },
    {
        "id": "FT-09", "category": "การสตาร์ท", "symptom": "บิดกุญแจแล้วเงียบสนิท ไม่มีเสียงใดๆ (No Crank / Silent)",
        "cause": "ไม่มีกระแสไฟฟ้าไหลเข้าโซลินอยด์สตาร์ท หรือแบตเตอรี่ไฟหมดเกลี้ยง",
        "system": "ระบบสตาร์ทและไฟฟ้า",
        "diagnostic": "1. วัดแรงดันแบตเตอรี่ (> 12.4V) 2. ตรวจฟิวส์สตาร์ทและรีเลย์",
        "action": "ชาร์จแบตเตอรี่, ขัดขั้วแบตเตอรี่ให้แน่น, เปลี่ยนสวิตช์กุญแจหรือรีเลย์สตาร์ท"
    },
    {
        "id": "FT-11", "category": "การสตาร์ท", "symptom": "ไดหมุนปกติแต่เครื่องไม่ติด มีลมในระบบ (Air in Fuel)",
        "cause": "มีฟองอากาศเล็ดลอดเข้าสู่ท่อทางเดินน้ำมันด้านแรงดันต่ำ ทำให้ปั๊มสร้างแรงดันไม่ได้",
        "system": "ระบบเชื้อเพลิง",
        "diagnostic": "1. สังเกตฟองอากาศในสายยางใส 2. กดปั๊มแย๊กมือดูว่ายวบหรือไม่",
        "action": "หาจุดรั่วตามข้อต่อท่อน้ำมัน โอริงกรองดักน้ำ แล้วทำการแย๊กไล่ลม (Bleeding)"
    },
    {
        "id": "FT-20", "category": "กำลังและสมรรถนะ", "symptom": "เครื่องยนต์เร่งรอบเองจนคุมไม่อยู่ (Diesel Engine Runaway)",
        "cause": "น้ำมันเครื่องรั่วเข้าท่อร่วมไอดีทางเทอร์โบ เครื่องยนต์ใช้น้ำมันเครื่องเป็นเชื้อเพลิง",
        "system": "ระบบหล่อลื่นและไอดี",
        "diagnostic": "1. สังเกตเครื่องยนต์เร่งรอบสุดขีด บิดกุญแจดับไม่ได้ และควันขาวท่วม",
        "action": "**วิกฤตสูงสุด:** หาทางอุดปิดปากท่อไอดีทันทีเพื่อตัดออกซิเจน! ห้ามใช้น้ำฉีด"
    },
    {
        "id": "FT-24", "category": "ความร้อนและของเหลว", "symptom": "น้ำมันเครื่องกลายเป็นสีกาแฟใส่นม (Emulsified / Milky Oil)",
        "cause": "น้ำหล่อเย็นรั่วผสมกับน้ำมันเครื่อง เกิดการกวนจนเป็นอิมัลชัน",
        "system": "ระบบหล่อลื่น / ระบายความร้อน",
        "diagnostic": "1. ชักก้านวัดน้ำมันเครื่องดูสี 2. ทดสอบแรงดันน้ำมันในออยล์คูลเลอร์",
        "action": "เปลี่ยนแผงไส้ออยล์คูลเลอร์ใหม่ หรือเปลี่ยนปะเก็นฝาสูบ พร้อมฟลัชชิ่งระบบน้ำมัน"
    },
    {
        "id": "FT-27", "category": "เสียงผิดปกติเชิงกล", "symptom": "เสียงเคาะตึ้กๆ ดังหนักแน่นใต้ท้องเครื่อง (Deep Heavy Knock / Rod Knock)",
        "cause": "ชาร์ปอกหรือชาร์ปก้านละลาย เกิดช่องว่างกระแทกเพลาข้อเหวี่ยงตามรอบ",
        "system": "กลไกเพลาข้อเหวี่ยงและก้านสูบ",
        "diagnostic": "1. ใช้หูฟังสเต็ทโทสโคปฟังตำแหน่งท้องอ่าง 2. ถอดกรองน้ำมันเครื่องตัดดูเศษทองแดง",
        "action": "**หยุดเครื่องทันที!** รื้ออ่างน้ำมันเครื่อง เจียรคอเพลาข้อเหวี่ยง เปลี่ยนชาร์ปใหม่"
    }
]

DTC_DB = {
    "P0087": {"spn": "SPN 94 FMI 1", "en": "Fuel Rail Pressure Too Low", "th": "แรงดันในรางคอมมอนเรลต่ำกว่าค่าเป้าหมาย", "action": "เช็กกรองดีเซลตัน, วัด Backleak หัวฉีด, เช็ก SCV"},
    "P0088": {"spn": "SPN 157 FMI 0", "en": "Fuel Rail Pressure Too High", "th": "แรงดันในรางคอมมอนเรลสูงเกินพิกัดความปลอดภัย", "action": "เช็ก SCV ค้างปิด, เซนเซอร์แรงดันรางเพี้ยน, ท่อไหลกลับตัน"},
    "P0299": {"spn": "SPN 102 FMI 18", "en": "Turbocharger Underboost Condition", "th": "แรงดันบูสต์เทอร์โบต่ำกว่าค่าที่กำหนด", "action": "สโมกเทสต์หาจุดรั่วท่ออินเตอร์คูลเลอร์, เช็กแกนเวสต์เกต/VGT"},
    "P0234": {"spn": "SPN 102 FMI 16", "en": "Turbocharger Overboost Condition", "th": "แรงดันบูสต์เทอร์โบสูงเกินขีดจำกัด", "action": "ตรวจโซลินอยด์ควบคุมเวสต์เกต, ล้างเขม่าครีบแปรผัน VGT"},
    "P0524": {"spn": "SPN 100 FMI 1", "en": "Engine Oil Pressure Too Low", "th": "แรงดันน้ำมันเครื่องต่ำเกินระดับวิกฤต", "action": "ดับเครื่องทันที! ตรวจระดับน้ำมัน, วัดแรงดันด้วยเกจช่าง, ตรวจชาร์ป"},
    "P0335": {"spn": "SPN 636 FMI 2", "en": "Crankshaft Position Sensor Circuit", "th": "สัญญาณเซนเซอร์ตำแหน่งเพลาข้อเหวี่ยงขาดหาย", "action": "วัดความต้านทานเซนเซอร์ (800-1200 Ohm), ทำความสะอาดปลายเซนเซอร์"},
    "P2463": {"spn": "SPN 3251 FMI 0", "en": "DPF Restriction Soot High", "th": "ปริมาณเขม่าสะสมในหม้อ DPF สูงเกินพิกัด", "action": "สั่งรัน Forced DPF Regeneration ด้วยเครื่องสแกน หรือถอดล้าง"}
}

def search_troubleshoot(query):
    print(f"\n--- ผลการค้นหาอาการเสีย: '{query}' ---")
    found = False
    for item in TROUBLESHOOT_DB:
        if query.lower() in item["symptom"].lower() or query.lower() in item["cause"].lower() or query.lower() in item["action"].lower() or query.lower() in item["category"].lower():
            found = True
            print(f"\n[{item['id']}] {item['symptom']}")
            print(f"  - หมวดหมู่: {item['category']} | ระบบ: {item['system']}")
            print(f"  - สาเหตุรากเหง้า: {item['cause']}")
            print(f"  - ขั้นตอนตรวจเช็ก: {item['diagnostic']}")
            print(f"  - แนวทางแก้ไข: {item['action']}")
    if not found:
        print("ไม่พบข้อมูลอาการเสียที่ตรงกับคำค้นหา")

def lookup_dtc(code):
    c = code.upper()
    print(f"\n--- ผลการค้นหารหัส DTC: '{c}' ---")
    if c in DTC_DB:
        data = DTC_DB[c]
        print(f"รหัส: {c} | มาตรฐาน SAE J1939: {data['spn']}")
        print(f"คำอธิบาย (TH): {data['th']}")
        print(f"คำอธิบาย (EN): {data['en']}")
        print(f"แนวทางแก้ไข: {data['action']}")
    else:
        print(f"ไม่พบรหัส {c} ในฐานข้อมูลเบื้องต้น")

def calc_cr(bore_mm, stroke_mm, vc_cc, cyl=1):
    vd_cc = (math.pi / 4.0) * ((bore_mm / 10.0) ** 2) * (stroke_mm / 10.0)
    cr = (vd_cc + vc_cc) / vc_cc
    total_displacement = (vd_cc * cyl) / 1000.0
    print(f"\n--- ผลการคำนวณอัตราส่วนกำลังอัด (Compression Ratio) ---")
    print(f"ขนาดกระบอกสูบ (Bore): {bore_mm} mm | ระยะชัก (Stroke): {stroke_mm} mm")
    print(f"ปริมาตรความจุกระบอกสูบเดี่ยว (Vd): {vd_cc:.2f} cc")
    print(f"ปริมาตรห้องเผาไหม้ (Vc): {vc_cc:.2f} cc")
    print(f"อัตราส่วนกำลังอัด (Compression Ratio): {cr:.2f} : 1")
    if cyl > 1:
        print(f"ความจุรวมเครื่องยนต์ ({cyl} สูบ): {total_displacement:.2f} ลิตร (L)")

def calc_power(rpm, torque_nm):
    kw = (2.0 * math.pi * rpm * torque_nm) / 60000.0
    hp = kw * 1.34102
    print(f"\n--- ผลการคำนวณกำลังเครื่องยนต์ (Brake Power) ---")
    print(f"ความเร็วรอบ: {rpm} RPM | แรงบิด: {torque_nm} N-m")
    print(f"กำลังเพลา: {kw:.2f} kW ({hp:.2f} แรงม้า / HP)")

def main():
    parser = argparse.ArgumentParser(description="Diesel Engine Diagnostic & Engineering Utility")
    subparsers = parser.add_subparsers(dest="command", help="คำสั่งที่ต้องการใช้งาน")

    p_search = subparsers.add_parser("search", help="ค้นหาอาการเสีย")
    p_search.add_argument("query", type=str, help="คำค้นหา เช่น ควันดำ, สตาร์ท, ชาร์ป")

    p_dtc = subparsers.add_parser("dtc", help="ค้นหารหัส DTC")
    p_dtc.add_argument("code", type=str, help="รหัสปัญหา เช่น P0087, P0299")

    p_cr = subparsers.add_parser("calc-cr", help="คำนวณอัตราส่วนกำลังอัด")
    p_cr.add_argument("--bore", type=float, required=True, help="ขนาดกระบอกสูบ (mm)")
    p_cr.add_argument("--stroke", type=float, required=True, help="ระยะชัก (mm)")
    p_cr.add_argument("--vc", type=float, required=True, help="ปริมาตรห้องเผาไหม้ (cc)")
    p_cr.add_argument("--cyl", type=int, default=4, help="จำนวนกระบอกสูบ")

    p_pow = subparsers.add_parser("calc-power", help="คำนวณกำลังและแรงม้า")
    p_pow.add_argument("--rpm", type=float, required=True, help="รอบเครื่อง (RPM)")
    p_pow.add_argument("--torque", type=float, required=True, help="แรงบิด (N-m)")

    args = parser.parse_args()
    if args.command == "search":
        search_troubleshoot(args.query)
    elif args.command == "dtc":
        lookup_dtc(args.code)
    elif args.command == "calc-cr":
        calc_cr(args.bore, args.stroke, args.vc, args.cyl)
    elif args.command == "calc-power":
        calc_power(args.rpm, args.torque)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
