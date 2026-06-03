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
/// Integration tests for POST /api/v1/monitoring/clients/{ref}/snapshots (CREDIT-203).
/// The Flask call is stubbed with an HttpMessageHandler and the DbContext is swapped to the EF Core
/// in-memory provider, so neither a live ML service nor PostgreSQL is needed. The faithful relational
/// persistence suite (Testcontainers, ≥6 tests) is CREDIT-205.
/// </summary>
public class SnapshotPersistenceTests
{
    // A contract-shaped Flask /predict/timeseries response: 4 windows (label null), increasing trends.
    private const string FlaskHappyBody = """
    {
      "snapshotDate": null,
      "trajectory": [
        { "window": "W0", "label": null, "predictions": { "randomForest": 0.18, "xgboost": 0.20, "lstm": 0.15 } },
        { "window": "W1", "label": null, "predictions": { "randomForest": 0.27, "xgboost": 0.29, "lstm": 0.24 } },
        { "window": "W2", "label": null, "predictions": { "randomForest": 0.41, "xgboost": 0.44, "lstm": 0.39 } },
        { "window": "W3", "label": null, "predictions": { "randomForest": 0.58, "xgboost": 0.61, "lstm": 0.55 } }
      ],
      "trends": {
        "randomForest": { "slope": 0.40, "alert": "INCREASING_RISK" },
        "xgboost":      { "slope": 0.41, "alert": "INCREASING_RISK" },
        "lstm":         { "slope": 0.40, "alert": "INCREASING_RISK" }
      }
    }
    """;

    private static WebApplicationFactory<Program> CreateFactory(
        Func<HttpRequestMessage, HttpResponseMessage> responder, string dbName)
    {
        return new WebApplicationFactory<Program>().WithWebHostBuilder(builder =>
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureTestServices(services =>
            {
                services.AddHttpClient<PythonModelClient>()
                    .ConfigurePrimaryHttpMessageHandler(() => new StubHttpMessageHandler(responder));

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

    [Fact]
    public async Task CreateSnapshot_HappyPath_Returns201_AndPersistsSnapshotPredictionsTrend()
    {
        await using var factory = CreateFactory(_ => JsonResponse(HttpStatusCode.OK, FlaskHappyBody), Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        var response = await client.PostAsJsonAsync("/api/v1/monitoring/clients/client-001/snapshots", new
        {
            snapshotDate = "2026-05-10",
            features = ValidFeatures()
        });

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);

        var body = await response.Content.ReadFromJsonAsync<SnapshotResponse>();
        Assert.NotNull(body);
        Assert.True(body!.SnapshotId > 0);
        Assert.Equal("client-001", body.ClientRef);
        Assert.Equal(new DateOnly(2026, 5, 10), body.SnapshotDate);
        Assert.Equal(4, body.Trajectory.Count);
        Assert.True(body.Persisted.ClientCreated);
        Assert.Equal(3, body.Persisted.PredictionIds.Count);
        Assert.Equal(3, body.Persisted.TrendIds.Count);

        // Verify the rows actually landed in the database.
        using var scope = factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        var dbClient = Assert.Single(await db.Clients.ToListAsync());
        Assert.Equal("client-001", dbClient.ExternalRef);

        var snapshot = Assert.Single(await db.Snapshots.ToListAsync());
        Assert.Equal(dbClient.Id, snapshot.ClientId);
        Assert.Equal(body.SnapshotId, snapshot.Id);
        Assert.Equal(100000, snapshot.LimitBal);

        var predictions = await db.Predictions.OrderBy(p => p.Id).ToListAsync();
        Assert.Equal(3, predictions.Count);
        Assert.All(predictions, p => Assert.Equal(snapshot.Id, p.SnapshotId));
        // W3 predictions from the Flask stub, all >= 0.5 → "DEFAULT".
        var rf = Assert.Single(predictions, p => p.ModelName == "randomForest");
        Assert.Equal(0.58, rf.DefaultProbability, 3);
        Assert.Equal("DEFAULT", rf.Label);
        Assert.Equal(0.55, Assert.Single(predictions, p => p.ModelName == "lstm").DefaultProbability, 3);

        var trends = await db.Trends.ToListAsync();
        Assert.Equal(3, trends.Count);
        Assert.All(trends, t => Assert.Equal(dbClient.Id, t.ClientId));
        Assert.All(trends, t => Assert.Equal("INCREASING_RISK", t.Alert));
        Assert.Equal(0.40, Assert.Single(trends, t => t.ModelName == "randomForest").Slope, 3);
    }

    [Fact]
    public async Task CreateSnapshot_DuplicateClientAndDate_Returns409Conflict()
    {
        await using var factory = CreateFactory(_ => JsonResponse(HttpStatusCode.OK, FlaskHappyBody), Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        object payload = new { snapshotDate = "2026-05-10", features = ValidFeatures() };

        var first = await client.PostAsJsonAsync("/api/v1/monitoring/clients/dup-client/snapshots", payload);
        Assert.Equal(HttpStatusCode.Created, first.StatusCode);

        var second = await client.PostAsJsonAsync("/api/v1/monitoring/clients/dup-client/snapshots", payload);
        Assert.Equal(HttpStatusCode.Conflict, second.StatusCode);

        var error = await second.Content.ReadFromJsonAsync<ErrorEnvelope>();
        Assert.Equal("CONFLICT", error!.Error.Code);

        // Only the first write persisted.
        using var scope = factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        Assert.Single(await db.Snapshots.ToListAsync());
        Assert.Equal(3, await db.Predictions.CountAsync());
    }

    [Fact]
    public async Task CreateSnapshot_SecondDateSameClient_AppendsSnapshot_ClientCreatedFalse()
    {
        await using var factory = CreateFactory(_ => JsonResponse(HttpStatusCode.OK, FlaskHappyBody), Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        var first = await client.PostAsJsonAsync("/api/v1/monitoring/clients/repeat-client/snapshots",
            new { snapshotDate = "2026-04-15", features = ValidFeatures() });
        Assert.Equal(HttpStatusCode.Created, first.StatusCode);
        var firstBody = await first.Content.ReadFromJsonAsync<SnapshotResponse>();
        Assert.True(firstBody!.Persisted.ClientCreated);

        var second = await client.PostAsJsonAsync("/api/v1/monitoring/clients/repeat-client/snapshots",
            new { snapshotDate = "2026-05-10", features = ValidFeatures() });
        Assert.Equal(HttpStatusCode.Created, second.StatusCode);
        var secondBody = await second.Content.ReadFromJsonAsync<SnapshotResponse>();
        Assert.False(secondBody!.Persisted.ClientCreated);

        using var scope = factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        Assert.Single(await db.Clients.ToListAsync());            // one client reused
        Assert.Equal(2, await db.Snapshots.CountAsync());          // two snapshots
        Assert.Equal(3, await db.Trends.CountAsync());             // trends upserted, not duplicated
    }

    [Fact]
    public async Task CreateSnapshot_InvalidFeatures_Returns400_AndPersistsNothing()
    {
        // Flask must not be called on validation failure.
        await using var factory = CreateFactory(
            _ => throw new InvalidOperationException("Flask must not be called on validation failure"),
            Guid.NewGuid().ToString());
        var client = factory.CreateClient();

        var response = await client.PostAsJsonAsync("/api/v1/monitoring/clients/bad-client/snapshots", new
        {
            features = ValidFeatures(age: 10) // out of [18, 100]
        });

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        var error = await response.Content.ReadFromJsonAsync<ErrorEnvelope>();
        Assert.Equal("VALIDATION_FAILED", error!.Error.Code);

        using var scope = factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        Assert.Empty(await db.Clients.ToListAsync());
        Assert.Empty(await db.Snapshots.ToListAsync());
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
