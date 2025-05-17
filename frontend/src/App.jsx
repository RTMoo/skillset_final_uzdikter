import { useState } from 'react';
import { uploadVideo } from './api';

function App() {
  const [email, setEmail] = useState('');
  const [video, setVideo] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!video || !email) {
      alert('Заполни оба поля');
      return;
    }

    const formData = new FormData();
    formData.append('email', email);
    formData.append('video', video);

    try {
      const response = await uploadVideo(formData);
      console.log('Успех:', response.data);
      alert('Успешно отправлено!');
    } catch (error) {
      console.error('Ошибка:', error);
      alert(error.detail || 'Ошибка отправки');
    }
  };

  return (
    <div className="bg-orange-100 w-full h-screen flex justify-center items-center">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl shadow-md space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border border-gray-300 p-2 rounded w-full"
          required
        />
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setVideo(e.target.files[0])}
          className="w-full"
          required
        />
        <button
          type="submit"
          className="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600"
        >
          Отправить
        </button>
      </form>
    </div>
  );
}

export default App;
