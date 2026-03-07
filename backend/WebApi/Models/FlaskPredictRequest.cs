using System.Text.Json.Serialization;

namespace WebApi.Models;

public class FlaskPredictRequest
{
    [JsonPropertyName("LIMIT_BAL")]
    public int LimitBal { get; set; }

    [JsonPropertyName("SEX")]
    public int Sex { get; set; }

    [JsonPropertyName("EDUCATION")]
    public int Education { get; set; }

    [JsonPropertyName("MARRIAGE")]
    public int Marriage { get; set; }

    [JsonPropertyName("AGE")]
    public int Age { get; set; }

    [JsonPropertyName("PAY_0")]
    public int Pay0 { get; set; }

    [JsonPropertyName("PAY_2")]
    public int Pay2 { get; set; }

    [JsonPropertyName("PAY_3")]
    public int Pay3 { get; set; }

    [JsonPropertyName("PAY_4")]
    public int Pay4 { get; set; }

    [JsonPropertyName("PAY_5")]
    public int Pay5 { get; set; }

    [JsonPropertyName("PAY_6")]
    public int Pay6 { get; set; }

    [JsonPropertyName("BILL_AMT1")]
    public decimal BillAmt1 { get; set; }

    [JsonPropertyName("BILL_AMT2")]
    public decimal BillAmt2 { get; set; }

    [JsonPropertyName("BILL_AMT3")]
    public decimal BillAmt3 { get; set; }

    [JsonPropertyName("BILL_AMT4")]
    public decimal BillAmt4 { get; set; }

    [JsonPropertyName("BILL_AMT5")]
    public decimal BillAmt5 { get; set; }

    [JsonPropertyName("BILL_AMT6")]
    public decimal BillAmt6 { get; set; }

    [JsonPropertyName("PAY_AMT1")]
    public decimal PayAmt1 { get; set; }

    [JsonPropertyName("PAY_AMT2")]
    public decimal PayAmt2 { get; set; }

    [JsonPropertyName("PAY_AMT3")]
    public decimal PayAmt3 { get; set; }

    [JsonPropertyName("PAY_AMT4")]
    public decimal PayAmt4 { get; set; }

    [JsonPropertyName("PAY_AMT5")]
    public decimal PayAmt5 { get; set; }

    [JsonPropertyName("PAY_AMT6")]
    public decimal PayAmt6 { get; set; }
}
