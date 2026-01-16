# C# WPF Desktop Application Template

## Overview
This folder contains a template for building a C# WPF desktop application that connects to the Power Trading API.

## Architecture

```
┌─────────────────────────────────────┐
│    WPF DESKTOP APPLICATION          │
│    - XAML UI                        │
│    - MVVM Pattern                   │
│    - Professional Design            │
└──────────────┬──────────────────────┘
               │ HTTP/REST API
┌──────────────▼──────────────────────┐
│    PYTHON FASTAPI BACKEND           │
│    localhost:8000                   │
└─────────────────────────────────────┘
```

## Features to Implement

### 1. Main Window (MainWindow.xaml)
- **Upload Section**
  - Drag & Drop Excel file support
  - File browser button
  - Upload progress indicator
  
- **Data Display**
  - DataGrid for transactions
  - Summary cards for key metrics
  - Tab control for Buy/Sell/Charges views
  
- **Charts & Visualization**
  - Time-series charts (using LiveCharts or OxyPlot)
  - Price trends
  - Volume analysis

### 2. Models (Models/)
```csharp
public class TradingData
{
    public string SchemaVersion { get; set; }
    public string TemplateId { get; set; }
    public string ClientId { get; set; }
    public Metadata Metadata { get; set; }
    public List<BuyTransaction> BuyTransactions { get; set; }
    public List<SellTransaction> SellTransactions { get; set; }
    public Charges Charges { get; set; }
    public Summary Summary { get; set; }
}

public class Metadata
{
    public string TradingDate { get; set; }
    public string DeliveryDate { get; set; }
    public string EntityId { get; set; }
    public string EntityName { get; set; }
    public string PortfolioCode { get; set; }
    public string PortfolioName { get; set; }
}

public class BuyTransaction
{
    public DateTime TimeBlockStart { get; set; }
    public DateTime TimeBlockEnd { get; set; }
    public double QuantityMw { get; set; }
    public double RatePerMwh { get; set; }
    public double Amount { get; set; }
}

// Similar classes for SellTransaction, Charges, Summary
```

### 3. Services (Services/)
```csharp
public class ApiService
{
    private readonly HttpClient _httpClient;
    private const string BaseUrl = "http://localhost:8000/api";

    public async Task<TradingData> UploadFileAsync(string filePath)
    {
        using var content = new MultipartFormDataContent();
        var fileContent = new ByteArrayContent(File.ReadAllBytes(filePath));
        content.Add(fileContent, "file", Path.GetFileName(filePath));
        
        var response = await _httpClient.PostAsync($"{BaseUrl}/upload", content);
        var json = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<ApiResponse>(json).Data;
    }

    public async Task<List<FileInfo>> GetFilesAsync()
    {
        var response = await _httpClient.GetAsync($"{BaseUrl}/files");
        var json = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<FileListResponse>(json).Files;
    }
}
```

### 4. ViewModels (ViewModels/)
```csharp
public class MainViewModel : INotifyPropertyChanged
{
    private readonly ApiService _apiService;
    private TradingData _currentData;
    
    public ICommand UploadCommand { get; }
    public ICommand RefreshCommand { get; }
    
    public ObservableCollection<BuyTransaction> BuyTransactions { get; set; }
    public ObservableCollection<SellTransaction> SellTransactions { get; set; }
    
    // Properties for binding to UI
    public string TradingDate { get; set; }
    public decimal NetAmount { get; set; }
    public int TotalBuyTransactions { get; set; }
    
    private async void UploadFile(object parameter)
    {
        var dialog = new OpenFileDialog
        {
            Filter = "Excel Files|*.xls;*.xlsx"
        };
        
        if (dialog.ShowDialog() == true)
        {
            IsLoading = true;
            try
            {
                _currentData = await _apiService.UploadFileAsync(dialog.FileName);
                LoadData();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
```

### 5. Sample XAML (MainWindow.xaml)
```xml
<Window x:Class="PowerTradingApp.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Power Trading Data - Enterprise Dashboard" 
        Height="800" Width="1400">
    
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>
        
        <!-- Header -->
        <Border Grid.Row="0" Background="#667eea" Padding="20">
            <StackPanel>
                <TextBlock Text="⚡ Power Trading Data Platform" 
                           FontSize="28" FontWeight="Bold" 
                           Foreground="White"/>
                <TextBlock Text="Enterprise Excel Parser &amp; Analytics" 
                           FontSize="14" Foreground="WhiteSmoke"/>
            </StackPanel>
        </Border>
        
        <!-- Upload Section -->
        <Border Grid.Row="1" Margin="20" Padding="20" 
                BorderBrush="#667eea" BorderThickness="2" 
                CornerRadius="10">
            <StackPanel>
                <Button Content="📤 Upload Excel File" 
                        Command="{Binding UploadCommand}"
                        Height="40" FontSize="16" 
                        Background="#667eea" Foreground="White"/>
                <TextBlock Text="{Binding StatusMessage}" 
                           Margin="0,10,0,0" 
                           HorizontalAlignment="Center"/>
            </StackPanel>
        </Border>
        
        <!-- Data Display -->
        <TabControl Grid.Row="2" Margin="20,0,20,20">
            <TabItem Header="📋 Summary">
                <!-- Summary cards grid -->
            </TabItem>
            <TabItem Header="📈 Buy Transactions">
                <DataGrid ItemsSource="{Binding BuyTransactions}" 
                          AutoGenerateColumns="False">
                    <DataGrid.Columns>
                        <DataGridTextColumn Header="Time Start" 
                                          Binding="{Binding TimeBlockStart}"/>
                        <DataGridTextColumn Header="Quantity (MW)" 
                                          Binding="{Binding QuantityMw}"/>
                        <DataGridTextColumn Header="Rate (₹/MWh)" 
                                          Binding="{Binding RatePerMwh}"/>
                        <DataGridTextColumn Header="Amount (₹)" 
                                          Binding="{Binding Amount}"/>
                    </DataGrid.Columns>
                </DataGrid>
            </TabItem>
            <!-- More tabs... -->
        </TabControl>
    </Grid>
</Window>
```

## NuGet Packages Required

```
Newtonsoft.Json - JSON parsing
LiveCharts.Wpf - Charts and visualization
MaterialDesignThemes - Modern UI components
```

## Getting Started

1. **Create new WPF project in Visual Studio**
   ```
   dotnet new wpf -n PowerTradingApp
   ```

2. **Install NuGet packages**
   ```
   Install-Package Newtonsoft.Json
   Install-Package LiveCharts.Wpf
   Install-Package MaterialDesignThemes
   ```

3. **Start the Python API**
   ```bash
   cd /path/to/api
   python -m uvicorn main:app --reload
   ```

4. **Run the WPF app**
   - Press F5 in Visual Studio

## API Endpoints to Use

- `POST /api/upload` - Upload and parse Excel file
- `GET /api/files` - List all parsed files
- `GET /api/data/{filename}` - Get specific parsed data
- `GET /api/summary/{filename}` - Get summary only
- `DELETE /api/data/{filename}` - Delete file

## Best Practices

1. **Use MVVM pattern** - Separate UI, logic, and data
2. **Async/await** - All API calls should be async
3. **Error handling** - Show user-friendly error messages
4. **Loading indicators** - Show progress during operations
5. **Data binding** - Use two-way binding for forms
6. **Dependency injection** - Use DI for services

## Contact
For C# development questions, refer to your WPF expertise!
