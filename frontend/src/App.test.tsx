import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import App from './App'

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {ui}
      </AuthProvider>
    </BrowserRouter>
  )
}

describe('App', () => {
  it('renders login page when not authenticated', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('Welcome to Prism Engine')).toBeInTheDocument()
    expect(screen.getByText('Login with Keycloak')).toBeInTheDocument()
    expect(screen.getByText('Demo Login')).toBeInTheDocument()
  })

  it('shows demo mode notice', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('Demo Mode:')).toBeInTheDocument()
  })
})