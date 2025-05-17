import axios from "axios";


const API_URL = "http://0.0.0.0:8000/api/";

const api = axios.create({
    baseURL: API_URL,
    withCredentials: true,
});

// Вспомогательная функция для запросов
export const request = async (method, url, data = {}) => {
    try {
        const response = await api({ method, url, data });
        return response;
    } catch (error) {
        throw error.response?.data || { detail: "Ошибка запроса" };
    }
};


export const uploadVideo = (data) => request("post", "upload_video/", data)