namespace WebApi.Models;

public class PredictResponse
{
    public ModelPrediction RandomForest { get; set; } = null!;
    public ModelPrediction Xgboost { get; set; } = null!;
    public ModelPrediction Lstm { get; set; } = null!;
}

public class ModelPrediction
{
    public double DefaultProbability { get; set; }
    public string Prediction { get; set; } = null!;
}
