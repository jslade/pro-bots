import axios from 'axios';

axios.defaults.headers.common["Content-Type"] = "application/json";
axios.defaults.headers.common["Accept"] = "application/json";
axios.defaults.headers.common["X-Requested-With"] = "XMLHttpRequest";
axios.defaults.headers.common["Cache-Control"] = "no-cache, no-store, must-revalidate";
axios.defaults.headers.common["Pragma"] = "no-cache";
axios.defaults.headers.common["Expires"] = "0";

const apiClient = axios.create({
  baseURL: '/api',
});

export const GET = async (endpoint, params = {}) => {
  try {
    const response = await apiClient.get(endpoint, { params });
    return response.data;
  } catch (error) {
    console.error('GET request failed:', error);
    throw error;
  }
};

export const POST = async (endpoint, data = {}, params = {}) => {
  try {
    const response = await apiClient.post(endpoint, data, { params });
    return response.data;
  } catch (error) {
    console.error('POST request failed:', error);
    throw error;
  }
};

export const PUT = async (endpoint, data = {}, params = {}) => {
  try {
    const response = await apiClient.put(endpoint, data, { params });
    return response.data;
  } catch (error) {
    console.error('PUT request failed:', error);
    throw error;
  }
};

export const PATCH = async (endpoint, data = {}, params = {}) => {
  try {
    const response = await apiClient.patch(endpoint, data, { params });
    return response.data;
  } catch (error) {
    console.error('PATCH request failed:', error);
    throw error;
  }
};

export const DELETE = async (endpoint, params = {}) => {
  try {
    const response = await apiClient.delete(endpoint, { params });
    return response.data;
  } catch (error) {
    console.error('DELETE request failed:', error);
    throw error;
  }
};
