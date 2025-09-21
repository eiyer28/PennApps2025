export default function Button({ text, link, onClick }) {
  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (link) {
      window.location.href = link;
    }
  };

  return (
    <div 
      style={{
        background: 'var(--maincolor)',
        color: 'white',
        padding: '12px 24px',
        borderRadius: '25px',
        cursor: 'pointer',
        display: 'inline-block',
        fontSize: '1rem',
        fontWeight: '600',
        transition: 'all 0.3s ease',
        border: 'none',
        textDecoration: 'none'
      }}
      onClick={handleClick}
      onMouseEnter={(e) => {
        e.target.style.background = 'var(--subcolor)';
        e.target.style.opacity = '0.9';
        e.target.style.transform = 'scale(1.05)';
      }}
      onMouseLeave={(e) => {
        e.target.style.background = 'var(--maincolor)';
        e.target.style.opacity = '1';
        e.target.style.transform = 'scale(1)';
      }}
    >
      {text}
    </div>
  );
}
