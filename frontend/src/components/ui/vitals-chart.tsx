import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { format } from "date-fns";

interface VitalsData {
  id: string;
  recordedAt: string;
  systolic?: number;
  diastolic?: number;
  heartRate?: number;
  bloodGlucose?: string;
  temperature?: string;
  weight?: string;
}

interface VitalsChartProps {
  data: VitalsData[];
  metric: "bp" | "heartRate" | "glucose" | "weight";
  className?: string;
}

export function VitalsChart({ data, metric, className }: VitalsChartProps) {
  const formatChartData = () => {
    return data.map((vital) => {
      const date = format(new Date(vital.recordedAt), "MM/dd");
      
      switch (metric) {
        case "bp":
          return {
            date,
            systolic: vital.systolic || null,
            diastolic: vital.diastolic || null,
          };
        case "heartRate":
          return {
            date,
            value: vital.heartRate || null,
          };
        case "glucose":
          return {
            date,
            value: vital.bloodGlucose ? parseFloat(vital.bloodGlucose) : null,
          };
        case "weight":
          return {
            date,
            value: vital.weight ? parseFloat(vital.weight) : null,
          };
        default:
          return { date };
      }
    }).reverse(); // Reverse to show chronological order
  };

  const chartData = formatChartData();

  const getChartTitle = () => {
    switch (metric) {
      case "bp": return "Blood Pressure Trend";
      case "heartRate": return "Heart Rate Trend";
      case "glucose": return "Blood Glucose Trend";
      case "weight": return "Weight Trend";
      default: return "Vitals Trend";
    }
  };

  const getYAxisLabel = () => {
    switch (metric) {
      case "bp": return "mmHg";
      case "heartRate": return "bpm";
      case "glucose": return "mg/dL";
      case "weight": return "lbs";
      default: return "";
    }
  };

  return (
    <div className={`bg-card p-6 rounded-lg border border-border shadow-sm ${className}`} data-testid={`chart-${metric}`}>
      <h3 className="text-lg font-semibold text-foreground mb-4">{getChartTitle()}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            label={{ value: getYAxisLabel(), angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            labelStyle={{ color: 'var(--foreground)' }}
            contentStyle={{ 
              backgroundColor: 'var(--card)', 
              border: '1px solid var(--border)',
              borderRadius: '8px'
            }}
          />
          
          {metric === "bp" ? (
            <>
              <Line 
                type="monotone" 
                dataKey="systolic" 
                stroke="hsl(var(--accent))" 
                strokeWidth={2}
                name="Systolic"
                connectNulls={false}
              />
              <Line 
                type="monotone" 
                dataKey="diastolic" 
                stroke="hsl(var(--primary))" 
                strokeWidth={2}
                name="Diastolic"
                connectNulls={false}
              />
            </>
          ) : (
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="hsl(var(--primary))" 
              strokeWidth={2}
              connectNulls={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
