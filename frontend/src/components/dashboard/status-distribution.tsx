"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import type { ClaimStatus } from '@/lib/api-client'

interface StatusDistributionProps {
  title: string
  description?: string
  data: Record<ClaimStatus, number>
}

const STATUS_COLORS: Record<ClaimStatus, string> = {
  PROCESSING: 'hsl(var(--chart-1))',
  OCR_REVIEW: 'hsl(var(--chart-2))',
  CLEANING: 'hsl(var(--chart-3))',
  ANONYMIZING: 'hsl(var(--chart-4))',
  ANONYMIZATION_REVIEW: 'hsl(var(--chart-5))',
  READY_FOR_ANALYSIS: 'hsl(var(--chart-1))',
  ANALYZING: 'hsl(var(--chart-2))',
  ANALYZED: 'hsl(var(--success))',
  FAILED: 'hsl(var(--destructive))',
}

export function StatusDistribution({ title, description, data }: StatusDistributionProps) {
  const chartData = Object.entries(data)
    .filter(([_, value]) => value > 0)
    .map(([status, value]) => ({
      name: status,
      value,
      color: STATUS_COLORS[status as ClaimStatus] || 'hsl(var(--muted))',
    }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  borderColor: 'hsl(var(--border))',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: 'hsl(var(--foreground))' }}
              />
              <Legend
                formatter={(value) => (
                  <span className="text-sm text-muted-foreground">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

