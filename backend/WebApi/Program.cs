using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebApi.Data;
using WebApi.Models;
using WebApi.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();

// Shape automatic model-validation failures (400) as the contract's ErrorEnvelope.
builder.Services.Configure<ApiBehaviorOptions>(options =>
{
    options.InvalidModelStateResponseFactory = context =>
    {
        var firstError = context.ModelState
            .FirstOrDefault(kvp => kvp.Value?.Errors.Count > 0);
        var field = firstError.Key;
        var message = firstError.Value?.Errors.FirstOrDefault()?.ErrorMessage
                      ?? "One or more validation errors occurred";
        var details = string.IsNullOrEmpty(field) ? null : new { field };
        return new BadRequestObjectResult(ErrorEnvelope.ValidationFailed(message, details));
    };
});
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "Credit Default Prediction API", Version = "v1" });
});

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins("http://localhost:5173")
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

// Register services
builder.Services.AddHttpClient<PythonModelClient>();
builder.Services.AddScoped<PredictionService>();
builder.Services.AddScoped<MonitoringService>();

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));

var app = builder.Build();

// Skip startup migration under the "Testing" environment so integration tests
// (WebApplicationFactory) can boot the host without a live PostgreSQL instance.
if (!app.Environment.IsEnvironment("Testing"))
{
    using var scope = app.Services.CreateScope();
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("AllowFrontend");
app.UseAuthorization();
app.MapControllers();

app.Run();

// Exposed so the test project's WebApplicationFactory<Program> can boot the host.
public partial class Program { }
