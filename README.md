<style>
  body {
    background: #070b14;
    color: #e5ecff;
  }

  .profile-shell {
    max-width: 1100px;
    margin: 24px auto;
    padding: 20px 16px 40px;
    border-radius: 28px;
    background: radial-gradient(circle at top, rgba(59,130,246,0.16), transparent 30%),
                linear-gradient(180deg, rgba(15,23,42,0.92), rgba(9,13,24,0.96));
    border: 1px solid rgba(148, 163, 184, 0.17);
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.45);
    position: relative;
    overflow: hidden;
  }

  .profile-shell::before {
    content: "";
    position: absolute;
    inset: -20% auto auto -10%;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(56,189,248,0.28), transparent 60%);
    filter: blur(18px);
    pointer-events: none;
  }

  .profile-shell img {
    transition: transform 0.25s ease, filter 0.25s ease, box-shadow 0.25s ease;
  }

  .profile-shell img:hover {
    transform: translateY(-2px) scale(1.02);
    filter: drop-shadow(0 0 18px rgba(56, 189, 248, 0.42));
  }

  .soft-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(96,165,250,0.8), transparent);
    margin: 18px 0 10px;
  }

  .focus-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 12px;
    list-style: none;
    padding: 0;
    margin: 16px 0 24px;
  }

  .focus-list li {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(96, 165, 250, 0.24);
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: 0 10px 20px rgba(15, 23, 42, 0.25);
    transition: transform 0.2s ease, border-color 0.2s ease;
  }

  .focus-list li:hover {
    transform: translateY(-2px);
    border-color: rgba(125, 211, 252, 0.8);
  }

  .tech-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
    align-items: center;
    margin-top: 12px;
  }

  .chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 7px 12px;
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.24);
    background: rgba(15, 23, 42, 0.72);
    color: #dbeafe;
    font-weight: 600;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  }

  .chip:hover {
    transform: translateY(-1px);
    border-color: rgba(96,165,250,0.8);
    box-shadow: 0 8px 22px rgba(59, 130, 246, 0.18);
  }

  .contact-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: flex-start;
    margin-top: 18px;
  }

  .contact-row a {
    display: inline-block;
    transition: transform 0.2s ease, filter 0.2s ease;
  }

  .contact-row a:hover {
    transform: translateY(-2px) scale(1.02);
    filter: drop-shadow(0 0 12px rgba(96, 165, 250, 0.45));
  }
</style>

<div class="profile-shell">
  <div align="center">
    <img src="https://raw.githubusercontent.com/Angel17jc/Angel17jc/main/assets/name.svg" width="480" alt="Angel Conforme" />
  </div>

  <br/>

  <div align="center">
    <img src="https://raw.githubusercontent.com/Angel17jc/Angel17jc/main/assets/banner.svg" width="100%" alt="Angel Conforme - Software Engineering Student" />
  </div>

  <div class="soft-divider"></div>

  <h2>👨‍💻 Sobre mí</h2>

  <p>
  ¡Hola! Soy <b>Software Developer</b> y estudiante de <b>Ingeniería de Software</b> en la
  <b>Universidad Laica Eloy Alfaro de Manabí (ULEAM)</b> 🇪🇨.
  </p>

  <p>
  Mi interés por el desarrollo de software fue creciendo a medida que descubrí que
  programar no se trata únicamente de escribir código, sino de entender problemas,
  diseñar soluciones y construir sistemas que puedan mantenerse y crecer con el tiempo.
  </p>

  <p>
  Una de las partes que más disfruto es pensar en la arquitectura antes de empezar a
desarrollar: definir responsabilidades, organizar componentes y tomar decisiones que
  permitan que un proyecto sea más claro, escalable y fácil de mantener.
  </p>

  <p>
  También creo en llevar las ideas a la práctica. Me gusta transformar diseños y
  conceptos en software funcional, buscando un equilibrio entre una buena planificación
y la capacidad de entregar resultados.
  </p>

  <b>🚀 Actualmente enfocado en:</b>

  <ul class="focus-list">
    <li><b>Frontend Development</b> — React, TypeScript, Vite y Tailwind CSS</li>
    <li><b>Backend Development</b> — Node.js, NestJS y Express</li>
    <li>APIs REST y arquitectura de aplicaciones</li>
    <li><b>Bases de datos</b> — PostgreSQL y SQL</li>
    <li>Clean Architecture y buenas prácticas de desarrollo</li>
  </ul>

  <h2>🛠️ Tech Stack</h2>

  <div align="center">
    <div class="tech-row">
      <span class="chip">💻 Frontend</span>
      <img src="https://skillicons.dev/icons?i=ts,react,nextjs,tailwind,vite&theme=dark" />
    </div>

    <div class="tech-row">
      <span class="chip">⚙️ Backend</span>
      <img src="https://skillicons.dev/icons?i=nodejs,nestjs,express,python,java,spring&theme=dark" />
    </div>

    <div class="tech-row">
      <span class="chip">🔗 APIs</span>
      <img src="https://skillicons.dev/icons?i=graphql&theme=dark" />
      <img src="https://img.shields.io/badge/REST-85EA2D?style=flat-square&logo=swagger&logoColor=black&labelColor=1a1a2e" />
      <img src="https://img.shields.io/badge/WebSockets-010101?style=flat-square&logo=socket.io&logoColor=white&labelColor=1a1a2e" />
    </div>

    <div class="tech-row">
      <span class="chip">🗄️ Datos</span>
      <img src="https://skillicons.dev/icons?i=postgres,supabase,firebase&theme=dark" />
      <img src="https://img.shields.io/badge/TypeORM-E83524?style=flat-square&logo=typeorm&logoColor=white&labelColor=1a1a2e" />
    </div>

    <div class="tech-row">
      <span class="chip">🐳 DevOps</span>
      <img src="https://skillicons.dev/icons?i=docker,git,githubactions,linux&theme=dark" />
    </div>

    <div class="tech-row">
      <span class="chip">🔐 Auth</span>
      <img src="https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white&labelColor=1a1a2e" />
      <img src="https://img.shields.io/badge/Passport.js-34E27A?style=flat-square&logo=passport&logoColor=black&labelColor=1a1a2e" />
    </div>
  </div>

  <div align="center">
    <p><b>También he trabajado con</b></p>
    <div class="tech-row">
      <img src="https://skillicons.dev/icons?i=kotlin,angular,mongodb,mysql,azure&theme=dark" height="40" />
    </div>
  </div>

  <br/>

  <div align="center">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Angel17jc/Angel17jc/output/github-snake-dark.svg" />
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Angel17jc/Angel17jc/output/github-snake.svg" />
      <img src="https://raw.githubusercontent.com/Angel17jc/Angel17jc/output/github-snake-dark.svg" width="100%" alt="snake" />
    </picture>
  </div>

  <br/>

  <h2>📫 Contacto</h2>

  <div class="contact-row">
    <a href="mailto:anchundiaangel129@gmail.com">
      <img src="https://img.shields.io/badge/Gmail-D14836?style=flat-square&logo=gmail&logoColor=white"/>
    </a>

    <a href="https://www.linkedin.com/in/angel-joshue-conforme-anchundiaa-5258a42a4/" target="_blank">
      <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin"/>
    </a>
  </div>
</div>
