export interface PredictRequest {
  limitBal: number;
  sex: number;
  education: number;
  marriage: number;
  age: number;
  pay0: number;
  pay2: number;
  pay3: number;
  pay4: number;
  pay5: number;
  pay6: number;
  billAmt1: number;
  billAmt2: number;
  billAmt3: number;
  billAmt4: number;
  billAmt5: number;
  billAmt6: number;
  payAmt1: number;
  payAmt2: number;
  payAmt3: number;
  payAmt4: number;
  payAmt5: number;
  payAmt6: number;
}

export interface ModelPrediction {
  defaultProbability: number;
  prediction: string;
}

export interface PredictResponse {
  randomForest: ModelPrediction;
  xgboost: ModelPrediction;
  lstm: ModelPrediction;
}
