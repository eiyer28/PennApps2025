export default function Card({ height, width, title, content, image, link }) {
  const handleClick = () => {
    if (link) {
      window.location.href = link;
    }
  };

  const cardStyle = {
    ...(width && { width }),
    ...(height && { height }),
    borderRadius: '8px',
    padding: '16px',
    cursor: link ? 'pointer' : 'default',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    transition: 'transform 0.2s, box-shadow 0.2s',
    backgroundColor: 'white',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between'
  };

  const hoverStyle = link ? {
    ':hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 8px rgba(0,0,0,0.15)'
    }
  } : {};

  return (
    <div 
      style={cardStyle} 
      onClick={handleClick}
      onMouseEnter={(e) => {
        if (link) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
        }
      }}
      onMouseLeave={(e) => {
        if (link) {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        }
      }}
    >
      <h3 style={{ margin: '0 0 8px 0', fontSize: '1.2rem', color: '#333' }}>
        {title}
      </h3>
      <p style={{ margin: 0, color: 'var(--textcolor)', lineHeight: '1.4' }}>
        {content}
      </p>
    </div>
  );
}