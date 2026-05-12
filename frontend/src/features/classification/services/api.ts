import { apiFetch } from "../../../api/client";
import type { WasteFindResponse } from "../../../types/waste";

export const findWaste = async (
  file: File,
  query: string,
  useSahi: boolean = false,
): Promise<WasteFindResponse> => {
  const formData = new FormData();
  formData.append("query", query);
  formData.append("file", file);
  formData.append("use_slicing", String(useSahi));

  return apiFetch<WasteFindResponse>("/api/v1/waste/find", {
    method: "POST",
    body: formData,
  });
};
