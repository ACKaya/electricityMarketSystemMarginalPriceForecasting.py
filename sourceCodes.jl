using Pkg
Pkg.add("DataFrames")
Pkg.add("CSV")
Pkg.add("Plots")
Pkg.add("PlotlyJS")
using DataFrames
using CSV
using Plots
using Statistics
plotlyjs() 

# Verileri CSV dosyasından yükleme
df = CSV.read("C:\\Users\\pc\\Desktop\\ack.csv", DataFrame)

# Virgüllü değerleri noktaya çeviren ve sütunları Float64'e dönüştüren fonksiyon
function convert_commas_to_dots!(df)
    for col in names(df)
        if col != "Tarih"  # "Tarih" sütunu dışındaki işlemleri yap
            if eltype(df[!, col]) <: AbstractString
                df[!, col] = replace.(df[!, col], "," => ".")
                df[!, col] = parse.(Float64, df[!, col])
            end
        end
    end
end

convert_commas_to_dots!(df)

# Ortalama yıllık yüzdesel artış oranlarını hesaplama fonksiyonu
function calculate_average_growth_rate(data, year_columns)
    growth_rates = []
    for i in 1:(length(year_columns) - 1)
        for month in 1:12
            previous_value = data[month, year_columns[i]]
            current_value = data[month, year_columns[i + 1]]
            growth_rate = (current_value - previous_value) / previous_value * 100
            push!(growth_rates, growth_rate)
        end
    end
    return mean(growth_rates)
end

# TEİAŞ'tan aldığım 2019-2020-2021-2022-2023 Yıllarına ait üretim ve tüketim verilerine ait sütunlar
production_columns = ["Uretim2019", "Uretim2020", "Uretim2021", "Uretim2022", "Uretim2023"]
consumption_columns = ["Tuketim2019", "Tuketim2020", "Tuketim2021", "Tuketim2022", "Tuketim2023"]

# Ortalama büyüme oranlarını hesaplama
avg_production_growth = calculate_average_growth_rate(df, production_columns)
avg_consumption_growth = calculate_average_growth_rate(df, consumption_columns)

# 2023 yılının son ay verileri
last_production = df[:, production_columns[end]]
last_consumption = df[:, consumption_columns[end]]

# Gelecek yıl için ortalama büyüme oranını kullanarak aylık tahminleri hesaplama
forecast_production = [last_production[i] * (1 + avg_production_growth / 100) for i in 1:12]
forecast_consumption = [last_consumption[i] * (1 + avg_consumption_growth / 100) for i in 1:12]

# Grafik çizimi
plot_title = "Electricity Supply and Demand Forecasts"
x_labels = df.Tarih
p = plot(x_labels, df.Uretim2023, label="2023 Electricity Supply", xlabel="Months", ylabel="GWh", title=plot_title, lw=2)
plot!(p, x_labels, df.Tuketim2023, label="2023 Electricity Demand", lw=2)
plot!(p, x_labels, forecast_production, label="Electricity Supply Forecast", lw=2, linestyle=:dash)
plot!(p, x_labels, forecast_consumption, label="Electricity Demand Forecast", lw=2, linestyle=:dash)
display(p)
