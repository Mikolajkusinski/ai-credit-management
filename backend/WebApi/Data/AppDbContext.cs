using Microsoft.EntityFrameworkCore;
using WebApi.Models.Entities;

namespace WebApi.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Client> Clients => Set<Client>();
    public DbSet<Snapshot> Snapshots => Set<Snapshot>();
    public DbSet<Prediction> Predictions => Set<Prediction>();
    public DbSet<Trend> Trends => Set<Trend>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Client>(e =>
        {
            e.Property(c => c.ExternalRef).IsRequired().HasMaxLength(64);
            e.HasIndex(c => c.ExternalRef).IsUnique();
            e.Property(c => c.CreatedAt).HasDefaultValueSql("NOW()");
        });

        modelBuilder.Entity<Snapshot>(e =>
        {
            e.HasOne(s => s.Client)
                .WithMany(c => c.Snapshots)
                .HasForeignKey(s => s.ClientId)
                .OnDelete(DeleteBehavior.Cascade);

            e.HasIndex(s => new { s.ClientId, s.SnapshotDate });
        });

        modelBuilder.Entity<Prediction>(e =>
        {
            e.Property(p => p.ModelName).IsRequired().HasMaxLength(32);
            e.Property(p => p.Label).IsRequired().HasMaxLength(16);

            e.HasOne(p => p.Snapshot)
                .WithMany(s => s.Predictions)
                .HasForeignKey(p => p.SnapshotId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<Trend>(e =>
        {
            e.Property(t => t.ModelName).IsRequired().HasMaxLength(32);
            e.Property(t => t.Alert).IsRequired().HasMaxLength(32);
            e.Property(t => t.ComputedAt).HasDefaultValueSql("NOW()");

            e.HasOne(t => t.Client)
                .WithMany(c => c.Trends)
                .HasForeignKey(t => t.ClientId)
                .OnDelete(DeleteBehavior.Cascade);

            e.HasIndex(t => new { t.ClientId, t.ModelName });
        });
    }
}
