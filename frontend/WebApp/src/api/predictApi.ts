import axios from 'axios';
import { PredictRequest, PredictResponse } from '../types/prediction';

const API_BASE_URL = 'http://localhost:5166/api';

export const predictDefault = async (data: PredictRequest): Promise<PredictResponse> => {
  const response = await axios.post<PredictResponse>(`${API_BASE_URL}/predict`, data);
  return response.data;
};
