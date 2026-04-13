using System.Text.Json.Serialization;

namespace WebApi.Models;

public class PredictResponse
{
    [JsonPropertyName("randomForest")]
    public ModelPrediction? RandomForest { get; set; }

    [JsonPropertyName("xgboost")]
    public ModelPrediction? Xgboost { get; set; }

    [JsonPropertyName("lstm")]
    public ModelPrediction? Lstm { get; set; }
}

public class ModelPrediction
{
    [JsonPropertyName("prediction")]
    public string? Prediction { get; set; }

    [JsonPropertyName("defaultProbability")]
    public double DefaultProbability { get; set; }
}