import { BASE_URL } from "@/config/app.config";

export async function checkHealth() {
  const response = await fetch(`${BASE_URL}/health`);
  return response.json();
}
