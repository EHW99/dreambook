export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center px-4 py-16">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold text-text mb-4 font-display">
          꿈꾸는 나
        </h1>
        <p className="text-lg text-text-light mb-8">
          아이의 꿈을 동화책으로 만들어주는 AI 서비스
        </p>
        <button className="bg-primary hover:bg-primary-dark text-white font-medium py-3 px-8 rounded-2xl shadow-soft transition-all duration-200 hover:shadow-hover">
          동화책 만들기
        </button>
      </div>
    </main>
  );
}
