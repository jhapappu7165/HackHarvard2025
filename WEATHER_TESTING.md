# Weather Feature Testing Guide

## Quick Start

### 1. Start Backend
```powershell
cd backend\weather
python main.py
```
Expected output: `Running on http://127.0.0.1:8080`

### 2. Verify Backend
Open browser: `http://localhost:8080/health`
Should see: `{"status": "healthy"}`

Test weather endpoint: `http://localhost:8080/weather/current`
Should return JSON with weather data

### 3. Start Frontend
```powershell
cd frontend
pnpm dev
```
Expected output: `Local: http://localhost:5173/`

### 4. Test Weather Page
1. Open `http://localhost:5173/`
2. Click **Weather** tab in sidebar (CloudSun icon)
3. Page should load with weather data

## Testing Checklist

### ✅ Visual Tests
- [ ] Hero section displays with colored gradient background
- [ ] Temperature is shown in large font
- [ ] Weather icon animates with pulse effect
- [ ] Location and timestamp are visible
- [ ] Four condition cards display correctly (Wind, Humidity, Pressure, Visibility)

### ✅ Functionality Tests
- [ ] Page loads without errors
- [ ] Weather data appears after loading
- [ ] Skeleton loaders show during data fetch
- [ ] Hourly forecast timeline is scrollable
- [ ] Clicking an hour updates the details below
- [ ] Selected hour is highlighted
- [ ] Weather suggestions appear at bottom

### ✅ Error Handling Tests
- [ ] Stop backend and refresh page
- [ ] Error alert appears with "Try again" button
- [ ] Clicking "Try again" attempts to refetch data
- [ ] Start backend and retry - should work

### ✅ Responsive Tests
- [ ] Open DevTools and toggle device toolbar
- [ ] Test on mobile viewport (375px)
- [ ] Test on tablet viewport (768px)
- [ ] Test on desktop viewport (1920px)
- [ ] All content should be readable and accessible

### ✅ Performance Tests
- [ ] Check Network tab - API called once on mount
- [ ] Wait 5 minutes - should auto-refresh
- [ ] Check Console for no errors
- [ ] Page should feel snappy and responsive

## Expected Behavior

### Loading State
1. Skeleton boxes appear
2. One large skeleton for hero section
3. Four smaller skeletons for condition cards

### Success State
1. Gradient background based on weather
2. Temperature and condition displayed
3. All metrics populated with real data
4. 24 hours of forecast data in timeline
5. 3-6 weather suggestions listed

### Error State
1. Red alert box appears
2. Error message displayed
3. "Try again" link available
4. Clicking link refetches data

## Common Issues & Fixes

### Issue: "Failed to fetch weather data"
**Fix**: Ensure backend is running on port 8080
```powershell
cd backend\weather
python main.py
```

### Issue: CORS errors in console
**Fix**: Backend should have CORS enabled. Check `main.py` for:
```python
from fastapi.middleware.cors import CORSMiddleware
```

### Issue: Weather page shows blank
**Fix**: Check browser console for errors. Likely backend is not responding.

### Issue: Icons not showing
**Fix**: Ensure `lucide-react` is installed:
```powershell
cd frontend
pnpm install lucide-react
```

### Issue: Styles look broken
**Fix**: Restart frontend dev server:
```powershell
# Press Ctrl+C to stop
pnpm dev
```

## Debugging Tips

### Check Backend Health
```powershell
curl http://localhost:8080/health
```

### Check Weather Endpoint
```powershell
curl http://localhost:8080/weather/current
```

### View Frontend Console Logs
1. Open DevTools (F12)
2. Go to Console tab
3. Look for error messages
4. Check Network tab for failed requests

### Verify Route Configuration
Check `frontend/src/components/layout/data/sidebar-data.ts`:
- Weather tab should point to `/apps`
- Icon should be `CloudSun`

## Test Scenarios

### Scenario 1: First Time User
1. Start both backend and frontend
2. Navigate to home page
3. Click Weather in sidebar
4. Should see weather data immediately

### Scenario 2: Network Failure
1. Weather page is loaded
2. Stop backend server
3. Wait 5 minutes for auto-refresh
4. Error alert should appear
5. Start backend
6. Click "Try again"
7. Data should load

### Scenario 3: Hour Selection
1. Weather page loaded with data
2. Scroll through hourly forecast
3. Click on hour at position 5
4. Details should update below
5. Selected hour should be highlighted

### Scenario 4: Mobile Experience
1. Open in mobile viewport
2. Hero section should be readable
3. Cards should stack vertically
4. Hourly forecast should scroll horizontally
5. All text should be legible

## Performance Benchmarks

### Expected Load Times
- Initial page load: < 2 seconds
- API response: < 1 second
- Skeleton to content: < 100ms
- Hour selection: Instant

### Expected Bundle Size
- Weather page chunk: < 50KB
- Icons: < 10KB
- Total JS: < 500KB

## Accessibility Tests

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Hourly forecast items are focusable
- [ ] Enter/Space activates hour selection
- [ ] Retry button is keyboard accessible

### Screen Reader
- [ ] Hero section announces weather
- [ ] Condition cards have proper labels
- [ ] Hourly items announce time and temp
- [ ] Suggestions are read in order

## Success Criteria

All tests pass when:
1. ✅ Weather data loads successfully
2. ✅ UI is visually appealing and animated
3. ✅ All interactions work smoothly
4. ✅ Error states handle gracefully
5. ✅ Mobile responsive design works
6. ✅ Performance is fast and snappy
7. ✅ Accessibility standards met
8. ✅ Auto-refresh works every 5 minutes

## Reporting Issues

If you encounter issues:

1. **Check Console**: Look for error messages
2. **Check Network**: Verify API calls are successful
3. **Check Backend**: Ensure weather service is running
4. **Document Steps**: Write down exact steps to reproduce
5. **Share Errors**: Copy error messages from console

## Next Steps After Testing

Once all tests pass:
1. Deploy backend to production
2. Update `BACKEND_URL` in frontend
3. Build frontend for production
4. Deploy frontend
5. Monitor error logs
6. Gather user feedback

---

**Happy Testing! 🌤️**
