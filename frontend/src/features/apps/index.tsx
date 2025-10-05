import { useState, useEffect } from 'react'
import { Cloud, CloudRain, Sun, CloudSun, Droplets } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'


import { API_CONFIG } from '@/config/api'

interface CurrentWeather {
  timestamp: string
  is_day: number
  cloudcover_percent: number
  shortwave_radiation_wm2: number
  temperature_c: number
  precip_prob_percent: number | null
  rain_mm: number
}

interface HourlyWeather {
  timestamp: string
  is_day: number
  cloudcover_percent: number
  shortwave_radiation_wm2: number
  temperature_c: number
  precip_prob_percent: number
  rain_mm: number
}

type WeatherCondition = 'sunny' | 'partly-cloudy' | 'cloudy' | 'rainy' | 'night'

function getWeatherCondition(data: CurrentWeather | HourlyWeather): WeatherCondition {
  if (!data.is_day) return 'night'
  if (data.precip_prob_percent !== null && data.precip_prob_percent >= 50) return 'rainy'
  if (data.rain_mm > 0) return 'rainy'
  if (data.shortwave_radiation_wm2 >= 500 && data.cloudcover_percent <= 40) return 'sunny'
  if (data.cloudcover_percent >= 70) return 'cloudy'
  return 'partly-cloudy'
}

function getWeatherGradient(condition: WeatherCondition): string {
  const gradients = {
    sunny: 'from-blue-400 via-cyan-300 to-yellow-200',
    'partly-cloudy': 'from-blue-400 via-gray-300 to-blue-200',
    cloudy: 'from-gray-400 via-gray-300 to-gray-200',
    rainy: 'from-gray-600 via-blue-400 to-gray-600',
    night: 'from-indigo-900 via-purple-900 to-black',
  }
  return gradients[condition]
}

function getWeatherIcon(condition: WeatherCondition) {
  const icons = {
    sunny: <Sun className="w-16 h-16 text-yellow-400 animate-pulse" />,
    'partly-cloudy': <CloudSun className="w-16 h-16 text-gray-400" />,
    cloudy: <Cloud className="w-16 h-16 text-gray-500" />,
    rainy: <CloudRain className="w-16 h-16 text-blue-400" />,
    night: <Cloud className="w-16 h-16 text-indigo-300" />,
  }
  return icons[condition]
}

function getWeatherSuggestion(data: CurrentWeather | HourlyWeather) {
  // High sun conditions
  if (data.is_day && data.shortwave_radiation_wm2 >= 500 && data.cloudcover_percent <= 40) {
    return {
      title: '☀️ Route Extra Load to Solar',
      description: 'Sun intensity is high and skies are clear. Shift deferrable loads to solar for this hour.',
      action: 'Open Energy Dashboard',
      link: '/',
    }
  }

  // Low sun or cloudy
  if (data.shortwave_radiation_wm2 <= 150 || data.cloudcover_percent >= 80) {
    return {
      title: '🔋 Limit Solar Reliance',
      description: 'Solar output will be limited. Prefer grid or stored reserves for critical services.',
      action: 'Open Energy Dashboard',
      link: '/',
    }
  }

  // Rain conditions
  if ((data.precip_prob_percent !== null && data.precip_prob_percent >= 50) || data.rain_mm > 0) {
    return {
      title: '🌧️ Traffic Advisory',
      description: 'Expect slower traffic and reduced visibility. Preemptively adjust signal timing or route around low-lying roads.',
      action: 'View Traffic',
      link: '/traffic',
    }
  }

  // Normal conditions
  return {
    title: '✅ Normal Conditions',
    description: 'Conditions are moderate. Keep default energy mix and traffic patterns.',
    action: 'Open Energy Dashboard',
    link: '/energy',
  }
}

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
}

function formatDate(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

export function Apps() {
  const [currentWeather, setCurrentWeather] = useState<CurrentWeather | null>(null)
  const [futureHourlyForecast, setFutureHourlyForecast] = useState<HourlyWeather[]>([])
  const [selectedHourIndex, setSelectedHourIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchWeatherData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch current weather
      const currentRes = await fetch(`${API_CONFIG.BASE_URL}/api/weather/openmeteo_current`)
      if (!currentRes.ok) throw new Error('Failed to fetch current weather')
      const currentData = await currentRes.json()
      const current = currentData.data // Extract data from Flask response (single object)

      // Fetch hourly forecast
      const forecastRes = await fetch(`${API_CONFIG.BASE_URL}/api/weather/openmeteo_forecast`)
      if (!forecastRes.ok) throw new Error('Failed to fetch forecast')
      const forecastData = await forecastRes.json()
      const forecast = forecastData.data || [] // Extract data from Flask response

      // Filter to only include current and future hours
      const now = new Date()
      const currentAndFutureHours = forecast.filter((hour: HourlyWeather) => {
        const hourTime = new Date(hour.timestamp)
        return hourTime >= now
      })

      setCurrentWeather(current)
      setFutureHourlyForecast(currentAndFutureHours)
      setSelectedHourIndex(0) // Default to current/first future hour
    } catch (err) {
      console.error('Weather fetch error:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch weather data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWeatherData()
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchWeatherData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const selectedHour = futureHourlyForecast[selectedHourIndex] || currentWeather
  const condition = selectedHour ? getWeatherCondition(selectedHour) : 'sunny'
  const suggestion = selectedHour ? getWeatherSuggestion(selectedHour) : null

  if (loading) {
    return (
      <div className="h-full w-full p-6 space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton className="h-64 w-full rounded-lg" />
            <Skeleton className="h-32 w-full rounded-lg" />
            <Skeleton className="h-24 w-full rounded-lg" />
          </div>
          <Skeleton className="h-64 w-full rounded-lg" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full w-full p-6 flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-red-500">Error Loading Weather</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
            <Button onClick={fetchWeatherData} className="w-full">
              Try Again
            </Button>
            <div className="text-sm text-muted-foreground space-y-2">
              <p>Make sure the main backend is running:</p>
              <code className="block bg-muted p-2 rounded text-xs">
                cd backend<br />
                python app.py
              </code>
              <p>Backend should be at: <strong>{API_CONFIG.BASE_URL}</strong></p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!currentWeather || !selectedHour) return null

  return (
    <div className="h-full w-full overflow-y-auto">
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Weather</h1>
            <p className="text-muted-foreground">Boston conditions and forecast</p>
          </div>
          <div className="text-right text-sm text-muted-foreground">
            <div>Boston, MA (42.36°N, 71.06°W)</div>
            <div>{formatDate(selectedHour.timestamp)}</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Weather Display */}
          <div className="lg:col-span-2 space-y-6">
            {/* Hero Section with Animated Background */}
            <Card className="overflow-hidden">
              <div className={`relative bg-gradient-to-br ${getWeatherGradient(condition)} p-8 transition-all duration-500`}>
                <div className="relative z-10 text-white">
                  <div className="flex items-center justify-between mb-6">
                    {getWeatherIcon(condition)}
                    <div className="text-right">
                      <div className="text-6xl font-bold">
                        {selectedHour.temperature_c.toFixed(1)}°C
                      </div>
                      <div className="text-xl opacity-90 capitalize">
                        {condition.replace('-', ' ')}
                      </div>
                    </div>
                  </div>
                  <div className="text-sm opacity-90">
                    {formatDate(selectedHour.timestamp)}
                  </div>
                </div>
              </div>
            </Card>

            {/* Current Conditions Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Cloud className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Cloud Cover</span>
                  </div>
                  <div className="text-2xl font-bold">{selectedHour.cloudcover_percent}%</div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Droplets className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Precip. Prob.</span>
                  </div>
                  <div className="text-2xl font-bold">
                    {selectedHour.precip_prob_percent ?? 0}%
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Sun className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Solar</span>
                  </div>
                  <div className="text-2xl font-bold">
                    {selectedHour.shortwave_radiation_wm2.toFixed(0)}
                  </div>
                  <div className="text-xs text-muted-foreground">W/m²</div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <CloudRain className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Rain</span>
                  </div>
                  <div className="text-2xl font-bold">
                    {selectedHour.rain_mm > 0 ? selectedHour.rain_mm.toFixed(1) : '0'}
                  </div>
                  <div className="text-xs text-muted-foreground">mm</div>
                </CardContent>
              </Card>
            </div>

            {/* Hourly Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Forecast</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {futureHourlyForecast.map((hour, index) => {
                    const isSelected = index === selectedHourIndex
                    const hourCondition = getWeatherCondition(hour)
                    const isCurrentHour = index === 0
                    return (
                      <button
                        key={hour.timestamp}
                        onClick={() => setSelectedHourIndex(index)}
                        className={`
                          flex-shrink-0 p-3 rounded-lg border-2 transition-all relative
                          ${isSelected
                            ? 'border-primary bg-primary/10 scale-105'
                            : 'border-transparent hover:border-primary/50 hover:bg-accent'
                          }
                        `}
                      >
                        {isCurrentHour && (
                          <div className="absolute -top-2 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-xs px-2 py-0.5 rounded-full font-semibold">
                            Now
                          </div>
                        )}
                        <div className="text-xs font-medium mb-1">
                          {formatTime(hour.timestamp)}
                        </div>
                        <div className="flex justify-center mb-1">
                          {hourCondition === 'sunny' && <Sun className="w-5 h-5 text-yellow-500" />}
                          {hourCondition === 'partly-cloudy' && <CloudSun className="w-5 h-5 text-gray-500" />}
                          {hourCondition === 'cloudy' && <Cloud className="w-5 h-5 text-gray-500" />}
                          {hourCondition === 'rainy' && <CloudRain className="w-5 h-5 text-blue-500" />}
                          {hourCondition === 'night' && <Cloud className="w-5 h-5 text-indigo-400" />}
                        </div>
                        <div className="text-sm font-bold">
                          {hour.temperature_c.toFixed(0)}°
                        </div>
                        {hour.precip_prob_percent > 0 && (
                          <div className="text-xs text-blue-500 mt-1">
                            {hour.precip_prob_percent}%
                          </div>
                        )}
                      </button>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Suggestions */}
          <div>
            {suggestion && (
              <Card>
                <CardHeader>
                  <CardTitle>Suggestions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg mb-2">{suggestion.title}</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      {suggestion.description}
                    </p>
                    <Button asChild className="w-full">
                      <a href={suggestion.link}>{suggestion.action}</a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}