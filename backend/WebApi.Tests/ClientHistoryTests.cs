using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using WebApi.Data;
using WebApi.Models;
using WebApi.Models.Entities;
using WebApi.Services;

namespace WebApi.Tests;

/// <summary>
/// Integration tests for GET /api/v1/monitoring/clients/{ref}/history (CREDIT-204). History is seeded
/// via the POST snapshots endpoint (CREDIT-203), so this exercises the full write→read loop. The Flask
/// call is stubbed and the DbContext is swapped to the EF Core in-memory provider — no live ML service
/// or PostgreSQL needed (same harness as SnapshotPersistenceTests).
/// </summary>
public class ClientHistoryTests
{
    // Contract-shaped Flask /predict/timeseries response: 4 windows, W3 = 0.58/0.61/0.55, increasing trends.
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

    private static WebApplicationFactory<Program> CreateFactory(string dbName)
    {
        return new WebApplicationFactory<Program>().WithWebHostBuilder(builder =>
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureTestServices(services =>
            {
                services.AddHttpClient<PythonModelClient>()
                    .ConfigurePrimaryHttpMessageHandler(() => new StubHttpMessageHandler(
                        _ => JsonResponse(HttpStatusCode.OK, FlaskHappyBody)));

                // Swap PostgreSQL for the in-memory provider (unique store per factory).
                services.RemoveAll(typeof(DbContextOptions<AppDbContext>));
                services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase(dbName));
            });
        });
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

    private static async Task PostSnapshot(HttpClient client, string clientRef, string date)
    {
        var response = await client.PostAsJsonAsync(
            $"/api/v1/monitoring/clients/{clientRef}/snapshots",
            new { snapshotDate = date, features = ValidFeatures() });
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    }

    [Fact]
    public async Task GetHistory_AfterThreeSnapshots_Returns200_WithPointsSortedByDate()
    {
        await using var factory = CreateFactory(Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        // Posted out of chronological order — the response must come back ascending by date.
        await PostSnapshot(client, "hist-client", "2026-05-24");
        await PostSnapshot(client, "hist-client", "2026-04-15");
        await PostSnapshot(client, "hist-client", "2026-05-10");

        var response = await client.GetAsync("/api/v1/monitoring/clients/hist-client/history");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var body = await response.Content.ReadFromJsonAsync<HistoryResponse>();
        Assert.NotNull(body);
        Assert.Equal("hist-client", body!.ClientRef);
        Assert.Equal(3, body.History.Count);

        // Ascending (oldest → newest).
        Assert.Equal(new DateOnly(2026, 4, 15), body.History[0].SnapshotDate);
        Assert.Equal(new DateOnly(2026, 5, 10), body.History[1].SnapshotDate);
        Assert.Equal(new DateOnly(2026, 5, 24), body.History[2].SnapshotDate);

        // Each point carries the persisted W3 predictions from the Flask stub.
        Assert.All(body.History, p =>
        {
            Assert.True(p.SnapshotId > 0);
            Assert.Equal(0.58, p.Predictions.RandomForest, 3);
            Assert.Equal(0.61, p.Predictions.Xgboost, 3);
            Assert.Equal(0.55, p.Predictions.Lstm, 3);
        });

        // Trends come from the persisted Trend rows (upserted on each snapshot).
        Assert.Equal("INCREASING_RISK", body.Trends.RandomForest.Alert);
        Assert.Equal(0.40, body.Trends.RandomForest.Slope, 3);
        Assert.Equal("INCREASING_RISK", body.Trends.Lstm.Alert);
    }

    [Fact]
    public async Task GetHistory_UnknownClient_Returns404_ClientNotFound()
    {
        await using var factory = CreateFactory(Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        var response = await client.GetAsync("/api/v1/monitoring/clients/does-not-exist/history");

        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        var error = await response.Content.ReadFromJsonAsync<ErrorEnvelope>();
        Assert.Equal("CLIENT_NOT_FOUND", error!.Error.Code);
    }

    [Fact]
    public async Task GetHistory_InvalidLimit_Returns400_ValidationFailed()
    {
        await using var factory = CreateFactory(Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        var response = await client.GetAsync("/api/v1/monitoring/clients/any-client/history?limit=0");

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        var error = await response.Content.ReadFromJsonAsync<ErrorEnvelope>();
        Assert.Equal("VALIDATION_FAILED", error!.Error.Code);
    }

    [Fact]
    public async Task GetHistory_WithDateRange_ReturnsOnlyInRangeSnapshots()
    {
        await using var factory = CreateFactory(Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        await PostSnapshot(client, "range-client", "2026-04-15");
        await PostSnapshot(client, "range-client", "2026-05-10");
        await PostSnapshot(client, "range-client", "2026-05-24");

        var response = await client.GetAsync(
            "/api/v1/monitoring/clients/range-client/history?from=2026-05-01&to=2026-05-15");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var body = await response.Content.ReadFromJsonAsync<HistoryResponse>();
        var point = Assert.Single(body!.History);
        Assert.Equal(new DateOnly(2026, 5, 10), point.SnapshotDate);
    }

    [Fact]
    public async Task GetHistory_ClientWithNoSnapshots_Returns200_EmptyHistory_StableTrends()
    {
        await using var factory = CreateFactory(Guid.NewGuid().ToString());

        // Seed a client with no snapshots directly (no endpoint creates a client without a snapshot).
        using (var scope = factory.Services.CreateScope())
        {
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            db.Clients.Add(new Client { ExternalRef = "empty-client" });
            await db.SaveChangesAsync();
        }

        var client = factory.CreateClient();
        var response = await client.GetAsync("/api/v1/monitoring/clients/empty-client/history");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var body = await response.Content.ReadFromJsonAsync<HistoryResponse>();
        Assert.NotNull(body);
        Assert.Equal("empty-client", body!.ClientRef);
        Assert.Empty(body.History);
        // No stored trends → neutral defaults.
        Assert.Equal("STABLE", body.Trends.RandomForest.Alert);
        Assert.Equal(0d, body.Trends.RandomForest.Slope);
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
