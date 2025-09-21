import Image from 'next/image';
import Button from './button.jsx';

export default function Card({ 
  height, 
  width, 
  title, 
  content, 
  image, 
  link, 
  showBorder = false, 
  titleFontSize = '1.2rem', 
  contentFontSize = '0.9rem',
  padding = '16px',
  button = null
}) {
  const handleClick = () => {
    if (link) {
      window.location.href = link;
    }
  };

  const cardStyle = {
    ...(width && { width }),
    ...(height && { height }),
    borderRadius: '8px',
    padding: '0',
    cursor: link ? 'pointer' : 'default',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    transition: 'transform 0.2s, box-shadow 0.2s',
    backgroundColor: 'white',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    ...(showBorder && { border: '1px solid #e0e0e0' }),
    ...({button})
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
      {image && (
        <div style={{ 
          height: '70%', 
          width: '100%', 
          position: 'relative',
          overflow: 'hidden'
        }}>
          <Image 
            src={image}
            alt={title}
            fill
            style={{ objectFit: 'cover' }}
          />
        </div>
      )}
      <div style={{ 
        padding: padding, 
        height: '30%',
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px', 
        textAlign: 'center' 
      }}>
        <h2 style={{ margin: 0, fontSize: titleFontSize, color: 'var(--textcolor)' }}>
          {title}
        </h2>
        <p style={{ margin: 0, color: 'var(--textcolor)', lineHeight: '1.4', fontSize: contentFontSize }}>
          {content}
        </p>
        {button && (
          <div style={{marginTop: '20px', display: 'flex', justifyContent: 'center'}}>
                  <Button text="Learn More" link="/learn-more" />
                </div>
        )}
      </div>
    </div>
  );
}