import '../styles/global.css';

export default function Loader({ fullscreen = false }) {
  if (fullscreen) {
    return (
      <div className="loader-fullscreen">
        <div className="spinner" />
      </div>
    );
  }
  return <div className="spinner" />;
}
