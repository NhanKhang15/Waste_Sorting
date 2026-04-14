import { useState } from "react";

export interface DetectedObject {
  label: string;
  confidence: number;
  bbox: number[];
  cropUrl: string; // Backend sẽ cung cấp URL ảnh đã cắt dựa trên bbox
}

export interface UseClassifyData {
    imageUrl: string;
    detectedObjects: DetectedObject[];
    dslCode: string;
    parseTree: any;
    result: string;
}

export const useClassify = () => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<UseClassifyData | null>(null);

    const classify = async (file: File, query: string) => {
    setLoading(true);
    console.log("Searching for:", query);
    // Giả lập gọi API (Mock API) - team Backend sẽ thay bằng axios call thật sau này
    setTimeout(() => {
      setData({
        imageUrl: URL.createObjectURL(file),
        detectedObjects: [
          { 
            label: 'bottle', 
            confidence: 0.89, 
            bbox: [20, 30, 40, 50],
            cropUrl: 'https://picsum.photos/200' // Thêm dữ liệu giả để test giao diện
          }
        ],
        dslCode: `item "bottle" material "plastic" confidence 0.89\nrule recyclable: material == "plastic"`,
        parseTree: {
          name: "Program",
          children: [{ name: "RuleStmt", children: [{ name: "Recyclable" }] }]
        },
        result: "Phân loại: Thùng nhựa - Cộng 10 điểm cho ID 18"
      });
      setLoading(false);
    }, 1500);
  };

  return { classify, data, loading };
};

