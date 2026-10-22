import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || ''

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        return config
      },
      (error: AxiosError) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  get<T>(url: string, config?: object) {
    return this.client.get<T>(url, config)
  }

  post<T>(url: string, data?: object, config?: object) {
    return this.client.post<T>(url, data, config)
  }

  patch<T>(url: string, data?: object, config?: object) {
    return this.client.patch<T>(url, data, config)
  }

  delete<T>(url: string, config?: object) {
    return this.client.delete<T>(url, config)
  }
}

export const api = new ApiClient()