import Head from 'next/head';
import Image from 'next/image';
import MenuBar from './menu-bar.jsx';
import Button from './button.jsx';
import styles from '../styles/Home.module.css';

export default function LearnMore() {
  const containerStyle = {
    backgroundColor: 'white',
    minHeight: '100vh',
    paddingTop: '80px'
  };

  const sectionStyle = {
    padding: '60px 40px',
    maxWidth: '1200px',
    margin: '0 auto'
  };

  const contentStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '40px',
    marginBottom: '60px'
  };

  const textStyle = {
    flex: 1,
    fontSize: '1.1rem',
    lineHeight: '1.6',
    color: 'var(--textcolor)'
  };

  const imageStyle = {
    flex: 1,
    textAlign: 'center'
  };

  return (
    <>
      <Head>
        <title>Learn More - CarbonChain</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <MenuBar />

      <div style={containerStyle}>
        <div style={sectionStyle}>
          <h1 className={styles.title} style={{textAlign: 'center', marginBottom: '40px'}}>
            Learn More About CarbonChain
          </h1>

          <div style={contentStyle}>
            <div style={textStyle}>
              <h2 className={styles.subtitle}>Our Mission</h2>
              <p>
                CarbonChain bridges the gap between those who want to fund sustainable development 
                and the innovative projects that can make a real difference. We believe that 
                transparency and accountability are key to creating meaningful environmental impact.
              </p>
            </div>
            <div style={imageStyle}>
              <Image 
                src="/assets/yzy.jpg"
                alt="Sustainable development"
                width={400}
                height={300}
                style={{borderRadius: '8px'}}
              />
            </div>
          </div>

          <div style={{...contentStyle, flexDirection: 'row-reverse'}}>
            <div style={textStyle}>
              <h2 className={styles.subtitle}>Blockchain Technology</h2>
              <p>
                Our platform utilizes blockchain as a regulatory structure to ensure complete 
                traceability and verification of project completion. Every dollar you spend 
                is tracked from start to finish, giving you confidence that your investment 
                is making a real impact.
              </p>
            </div>
            <div style={imageStyle}>
              <Image 
                src="/assets/yzy.jpg"
                alt="Blockchain technology"
                width={400}
                height={300}
                style={{borderRadius: '8px'}}
              />
            </div>
          </div>

          <div style={contentStyle}>
            <div style={textStyle}>
              <h2 className={styles.subtitle}>Verified Projects</h2>
              <p>
                All projects on our platform undergo rigorous verification processes. 
                We work with certified organizations and use advanced monitoring systems 
                to ensure that every carbon offset purchase leads to genuine environmental benefits.
              </p>
            </div>
            <div style={imageStyle}>
              <Image 
                src="/assets/yzy.jpg"
                alt="Environmental projects"
                width={400}
                height={300}
                style={{borderRadius: '8px'}}
              />
            </div>
          </div>

          <div style={{textAlign: 'center', marginTop: '60px'}}>
            <h2 className={styles.subtitle} style={{marginBottom: '20px'}}>
              Ready to Make an Impact?
            </h2>
            <p style={{fontSize: '1.1rem', marginBottom: '30px', color: 'var(--textcolor)'}}>
              Explore our verified projects and start offsetting your carbon footprint today.
            </p>
            <Button text="Get Started" link="/search" />
          </div>
        </div>
      </div>
    </>
  );
}
