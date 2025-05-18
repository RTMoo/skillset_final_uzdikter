import { useState } from 'react';
import { uploadVideo } from './api';

function App() {
  const [email, setEmail] = useState('');
  const [video, setVideo] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!video || !email) {
      alert('Заполни оба поля');
      return;
    }

    const formData = new FormData();
    formData.append('email', email);
    formData.append('video', video);

    setIsSubmitting(true);

    try {
      const response = await uploadVideo(formData);
      console.log('Успех:', response.data);
      alert('Успешно отправлено!');
    } catch (error) {
      console.error('Ошибка:', error);
      alert(error.detail || 'Ошибка отправки');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-orange-100 w-full h-screen flex justify-center items-center px-4">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md space-y-6">
        {/* Лого и заголовок */}
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600 mb-1">🎬 Edu Highlights Analyzer</div>
          <p className="text-gray-500 text-sm">Загрузи видео и получи ключевые моменты</p>
        </div>

        {/* Форма */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              placeholder="example@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="border border-gray-300 p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-orange-400"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Видео</label>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setVideo(e.target.files[0])}
              className="w-full text-sm"
              required
            />
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full text-white px-4 py-2 rounded transition ${
              isSubmitting
                ? 'bg-orange-300 cursor-not-allowed'
                : 'bg-orange-500 hover:bg-orange-600'
            }`}
          >
            {isSubmitting ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
