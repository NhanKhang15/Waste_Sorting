import { apiFetch } from "../../../api/client";
import type { WasteFindResponse } from "../../../types/waste";

export const findWaste = async (
  file: File,
  query: string,
): Promise<WasteFindResponse> => {
  const formData = new FormData();
  formData.append("query", query);
  formData.append("file", file);

  return apiFetch<WasteFindResponse>("/api/v1/waste/find", {
    method: "POST",
    body: formData,
  });
};
