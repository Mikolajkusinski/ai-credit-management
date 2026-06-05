using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using WebApi.Models;
using WebApi.Services;

namespace WebApi.Tests;

/// <summary>
/// Integration tests for POST /api/v1/monitoring/predict-timeseries (CREDIT-202).
/// The Flask call is intercepted with a stub HttpMessageHandler so no live ML service is needed.
/// </summary>
public class MonitoringTimeseriesTests
{
    // A contract-shaped Flask /predict/timeseries response: 4 windows (label null), increasing trends.
    private const string FlaskHappyBody = """
    {
      "snapshotDate": null,
      "trajectory": [
        { "window": "W0", "label": null, "predictions": { "randomForest": 0.18, "xgboost": 0.20, "lightgbm": 0.19, "catboost": 0.17, "lstm": 0.15 } },
        { "window": "W1", "label": null, "predictions": { "randomForest": 0.27, "xgboost": 0.29, "lightgbm": 0.28, "catboost": 0.26, "lstm": 0.24 } },
        { "window": "W2", "label": null, "predictions": { "randomForest": 0.41, "xgboost": 0.44, "lightgbm": 0.42, "catboost": 0.40, "lstm": 0.39 } },
        { "window": "W3", "label": null, "predictions": { "randomForest": 0.58, "xgboost": 0.61, "lightgbm": 0.60, "catboost": 0.57, "lstm": 0.55 } }
      ],
      "trends": {
        "randomForest": { "slope": 0.40, "alert": "INCREASING_RISK" },
        "xgboost":      { "slope": 0.41, "alert": "INCREASING_RISK" },
        "lightgbm":     { "slope": 0.41, "alert": "INCREASING_RISK" },
        "catboost":     { "slope": 0.40, "alert": "INCREASING_RISK" },
        "lstm":         { "slope": 0.40, "alert": "INCREASING_RISK" }
      }
    }
    """;

    private static HttpClient CreateClient(Func<HttpRequestMessage, HttpResponseMessage> responder)
    {
        var factory = new WebApplicationFactory<Program>().WithWebHostBuilder(builder =>
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureTestServices(services =>
            {
                services.AddHttpClient<PythonModelClient>()
                    .ConfigurePrimaryHttpMessageHandler(() => new StubHttpMessageHandler(responder));
            });
        });
        return factory.CreateClient();
    }

    private static object ValidFeatures(int age = 35) => new
    {
        limitBal = 100000,
        sex = 1,
        education = 2,
        marriage = 1,
        age,
        pay0 = 0, pay2 = 0, pay3 = 0, pay4 = 0, pay5 = 0, pay6 = 0,
        billAmt1 = 50000, billAmt2 = 48000, billAmt3 = 46000,
        billAmt4 = 44000, billAmt5 = 42000, billAmt6 = 40000,
        payAmt1 = 5000, payAmt2 = 5000, payAmt3 = 5000,
        payAmt4 = 5000, payAmt5 = 5000, payAmt6 = 5000
    };

    [Fact]
    public async Task PredictTimeseries_HappyPath_Returns200WithLabelledTrajectoryAndTrends()
    {
        var client = CreateClient(_ => JsonResponse(HttpStatusCode.OK, FlaskHappyBody));

        var response = await client.PostAsJsonAsync("/api/v1/monitoring/predict-timeseries", new
        {
            clientRef = "client-001",
            snapshotDate = "2026-08-15",
            features = ValidFeatures()
        });

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var body = await response.Content.ReadFromJsonAsync<TimeseriesResponse>();
        Assert.NotNull(body);
        Assert.Equal("client-001", body!.ClientRef);
        Assert.Equal(new DateOnly(2026, 8, 15), body.SnapshotDate);

        Assert.Equal(4, body.Trajectory.Count);
        Assert.Equal(new[] { "W0", "W1", "W2", "W3" }, body.Trajectory.Select(p => p.Window).ToArray());

        // Labels computed by the backend from snapshotDate (contract section 2.2).
        Assert.Equal("Mar-May 2026", body.Trajectory[0].Label);
        Assert.Equal("Apr-Jun 2026", body.Trajectory[1].Label);
        Assert.Equal("May-Jul 2026", body.Trajectory[2].Label);
        Assert.Equal("Jun-Aug 2026", body.Trajectory[3].Label);

        // Predictions mapped through from Flask.
        Assert.Equal(0.58, body.Trajectory[3].Predictions.RandomForest, 3);
        Assert.Equal(0.55, body.Trajectory[3].Predictions.Lstm, 3);

        // Trends passed through from Flask.
        Assert.Equal("INCREASING_RISK", body.Trends.RandomForest.Alert);
        Assert.Equal(0.40, body.Trends.RandomForest.Slope, 3);
        Assert.Equal("INCREASING_RISK", body.Trends.Lstm.Alert);
    }

    [Fact]
    public async Task PredictTimeseries_InvalidFeatures_Returns400ValidationFailed()
    {
        // Flask should never be called; if it is, fail loudly.
        var client = CreateClient(_ => throw new InvalidOperationException("Flask must not be called on validation failure"));

        var response = await client.PostAsJsonAsync("/api/v1/monitoring/predict-timeseries", new
        {
            clientRef = "client-001",
            features = ValidFeatures(age: 10) // out of [18, 100]
        });

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        var error = await response.Content.ReadFromJsonAsync<ErrorEnvelope>();
        Assert.NotNull(error);
        Assert.Equal("VALIDATION_FAILED", error!.Error.Code);
    }

    [Fact]
    public async Task PredictTimeseries_FlaskReturns500_Returns502MlServiceError()
    {
        var client = CreateClient(_ => JsonResponse(HttpStatusCode.InternalServerError,
            """{ "error": { "code": "INTERNAL_ERROR", "message": "boom" } }"""));

        var response = await client.PostAsJsonAsync("/api/v1/monitoring/predict-timeseries", new
        {
            features = ValidFeatures()
        });

        Assert.Equal(HttpStatusCode.BadGateway, response.StatusCode);
        var error = await response.Content.ReadFromJsonAsync<ErrorEnvelope>();
        Assert.Equal("ML_SERVICE_ERROR", error!.Error.Code);
    }

    [Fact]
    public async Task PredictTimeseries_FlaskUnreachable_Returns503MlServiceUnavailable()
    {
        var client = CreateClient(_ => throw new HttpRequestException("connection refused"));

        var response = await client.PostAsJsonAsync("/api/v1/monitoring/predict-timeseries", new
        {
            features = ValidFeatures()
        });

        Assert.Equal(HttpStatusCode.ServiceUnavailable, response.StatusCode);
        var error = await response.Content.ReadFromJsonAsync<ErrorEnvelope>();
        Assert.Equal("ML_SERVICE_UNAVAILABLE", error!.Error.Code);
    }

    private static HttpResponseMessage JsonResponse(HttpStatusCode status, string json) =>
        new(status) { Content = new StringContent(json, System.Text.Encoding.UTF8, "application/json") };

    private sealed class StubHttpMessageHandler : HttpMessageHandler
    {
        private readonly Func<HttpRequestMessage, HttpResponseMessage> _responder;

        public StubHttpMessageHandler(Func<HttpRequestMessage, HttpResponseMessage> responder) => _responder = responder;

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) =>
            Task.FromResult(_responder(request));
    }
}
