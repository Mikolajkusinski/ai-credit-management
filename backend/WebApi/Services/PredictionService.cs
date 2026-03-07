using WebApi.Models;

namespace WebApi.Services;

public class PredictionService
{
    private readonly PythonModelClient _pythonModelClient;
    private readonly ILogger<PredictionService> _logger;

    public PredictionService(PythonModelClient pythonModelClient, ILogger<PredictionService> logger)
    {
        _pythonModelClient = pythonModelClient;
        _logger = logger;
    }

    public async Task<PredictResponse?> PredictAsync(PredictRequest request)
    {
        // Validate input
        ValidateRequest(request);

        // Map to Flask request format
        var flaskRequest = new FlaskPredictRequest
        {
            LimitBal = request.LimitBal,
            Sex = request.Sex,
            Education = request.Education,
            Marriage = request.Marriage,
            Age = request.Age,
            Pay0 = request.Pay0,
            Pay2 = request.Pay2,
            Pay3 = request.Pay3,
            Pay4 = request.Pay4,
            Pay5 = request.Pay5,
            Pay6 = request.Pay6,
            BillAmt1 = request.BillAmt1,
            BillAmt2 = request.BillAmt2,
            BillAmt3 = request.BillAmt3,
            BillAmt4 = request.BillAmt4,
            BillAmt5 = request.BillAmt5,
            BillAmt6 = request.BillAmt6,
            PayAmt1 = request.PayAmt1,
            PayAmt2 = request.PayAmt2,
            PayAmt3 = request.PayAmt3,
            PayAmt4 = request.PayAmt4,
            PayAmt5 = request.PayAmt5,
            PayAmt6 = request.PayAmt6
        };

        _logger.LogInformation("Sending prediction request to Python service");
        return await _pythonModelClient.GetPredictionsAsync(flaskRequest);
    }

    private void ValidateRequest(PredictRequest request)
    {
        if (request.LimitBal < 10000 || request.LimitBal > 1000000)
            throw new ArgumentException("LimitBal must be between 10,000 and 1,000,000");

        if (request.Sex < 1 || request.Sex > 2)
            throw new ArgumentException("Sex must be 1 (Male) or 2 (Female)");

        if (request.Education < 1 || request.Education > 4)
            throw new ArgumentException("Education must be between 1 and 4");

        if (request.Marriage < 1 || request.Marriage > 3)
            throw new ArgumentException("Marriage must be between 1 and 3");

        if (request.Age < 18 || request.Age > 100)
            throw new ArgumentException("Age must be between 18 and 100");

        var payFields = new[] { request.Pay0, request.Pay2, request.Pay3, request.Pay4, request.Pay5, request.Pay6 };
        foreach (var pay in payFields)
        {
            if (pay < -2 || pay > 9)
                throw new ArgumentException("Payment status must be between -2 and 9");
        }

        var payAmounts = new[] { request.PayAmt1, request.PayAmt2, request.PayAmt3, request.PayAmt4, request.PayAmt5, request.PayAmt6 };
        foreach (var amount in payAmounts)
        {
            if (amount < 0)
                throw new ArgumentException("Payment amounts must be non-negative");
        }
    }
}
