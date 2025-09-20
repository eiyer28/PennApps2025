import Head from "next/head";
import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import styles from "@/styles/Home.module.css";
import { useEffect, useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import Card from "./card.jsx";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// useLayoutEffect(() => {
//   const context = gsap.context(() => {
//     const tl = gasp.timeline() ({
//       scrollTrigger: {
//         target: container.current,
//         start: "top bottom",
//         end: "bottom",
//         scrub: true
//       }
//     });


// }, []));

export default function Home() {
  const title = useRef(null);
  
  return ( 
    <>
      <Head>
        <title>CarbonChain</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div style={{backgroundColor: 'white'}}>
        <div className={styles.fullsection} style={{backgroundColor: 'white'}}>
          <h1 className={styles.title} ref={title}>
            Offset your carbon footprint, <br />
            know you're having an impact
          </h1>
          <p className={styles.landingbody}>
            Let's get started
          </p>
        </div>

        <div className={styles.fullsection}>
          <h2 className={styles.subtitle}>
            About us
          </h2>
          <p className={styles.landingbody}>
            Those with the money that can fund sustainable development 
            are not being connected with the people and places that are 
            engineering the solutions that can meaningfully affect our 
            own carbon output and our own development of our cities and 
            societies.

            We aim to solve this problem by creating a platform that utilizes
            blockchain as a regulatory structure to ensure traceability 
            and completion of these projects. 
          </p>
          <button>
            learn more about our work
          </button>
        </div>

        <div className={styles.fullsection} style={{backgroundColor: 'var(--maincolor)'}}>
          <h2 className={styles.subtitle}>
            Start here, start now
          </h2>
          <div className={styles.cardgrids}>
            <Card 
            height="250px"
            width="300px"
            title="Buy Carbon Offsets"
            content="Browse possible projects to support and offset your carbon footprint, starting as small as a few cents."
            link="/projects"
            />
            <Card 
              height="250px"
              width="300px"
              title="Supply Projects"
              content="Support verified sustainable development projects around the world."
              link="/supply-projects"
            />
          </div>
        </div>
      </div>
    </>
  );
}
