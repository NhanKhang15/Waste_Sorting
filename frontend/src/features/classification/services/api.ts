import { apiRequest } from "../../../api/client";
import type {
  DetectionResponse,
  HealthResponse,
  ModelStatusResponse,
} from "../../../types/waste";

export async function detectWaste(file: File): Promise<DetectionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest<DetectionResponse>("/yolov26/detect", {
    method: "POST",
    body: formData,
  });
}

export async function getModelStatus(): Promise<ModelStatusResponse> {
  return apiRequest<ModelStatusResponse>("/yolov26/model");
}

export async function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/healthz");
}
