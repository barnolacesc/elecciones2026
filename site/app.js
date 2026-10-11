/**
 * Elecciones 2026 — Public Comparison & Selection Interaction
 * Pure vanilla JavaScript with zero external CDN dependencies.
 * Compliant with WCAG 2.2 AA (touch/keyboard accessible).
 * Handles:
 *  - One-topic and two-party selection validation (rejects identical parties).
 *  - Comparison grouped by measure with short summary and both party positions per measure.
 *  - Visible source citations, exact locators, and qualifications/caveats.
 *  - Strict zero tabs: both parties visible before the next measure without tab switching.
 *  - Explicit negative/missing state ("No consta en el programa") never conflated with opposition.
 *  - URL query state synchronization and deep linking (?topic=...&partyA=...&partyB=...).
 *  - Neutral copy and native share fallback.
 *  - Strict zero visitor profiles, no data collection.
 */

(function () {
  'use strict';

  // 8 Core topics defined in taxonomy 1.0.0
  const TOPICS = {
    'housing': {
      id: 'housing',
      name: 'Vivienda',
      description: 'Políticas de oferta residencial, contención de alquileres y acceso a la vivienda.'
    },
    'education': {
      id: 'education',
      name: 'Educación',
      description: 'Políticas de financiación del sistema educativo, centros concertados y plazas públicas.'
    },
    'health-social-services': {
      id: 'health-social-services',
      name: 'Sanidad y servicios sociales',
      description: 'Inversión en el Sistema Nacional de Salud, dotación de personal y cobertura de salud mental.'
    },
    'economy-work-tax': {
      id: 'economy-work-tax',
      name: 'Economía, trabajo y fiscalidad',
      description: 'Políticas laborales, fijación del salario mínimo, jornada y sostenibilidad fiscal.'
    },
    'immigration': {
      id: 'immigration',
      name: 'Inmigración',
      description: 'Gestión de flujos migratorios, procedimientos de asilo y cooperación en origen.'
    },
    'foreign-policy-eu': {
      id: 'foreign-policy-eu',
      name: 'Política exterior y UE',
      description: 'Cumplimiento de objetivos de gasto en defensa y acuerdos comunitarios.'
    },
    'climate-energy': {
      id: 'climate-energy',
      name: 'Clima y energía',
      description: 'Transición energética, infraestructura de red y calendario de descarbonización.'
    },
    'institutions-rights': {
      id: 'institutions-rights',
      name: 'Instituciones, justicia y derechos fundamentales',
      description: 'Reformas institucionales, sistema de elección del CGPJ y modelo territorial.'
    }
  };

  // Qualified candidacies and test fixtures
  const PARTIES = {
    'party-a': {
      id: 'party-a',
      name: 'Partido A',
      shortName: 'Partido A',
      pill: 'A',
      pillClass: 'party-pill-a',
      status: 'official',
      statusLabel: 'Programa oficial',
      isFixture: true
    },
    'party-b': {
      id: 'party-b',
      name: 'Partido B',
      shortName: 'Partido B',
      pill: 'B',
      pillClass: 'party-pill-b',
      status: 'partial',
      statusLabel: 'Documento parcial',
      isFixture: true
    },
    'coalicion-c': {
      id: 'coalicion-c',
      name: 'Coalición C',
      shortName: 'Coalición C',
      pill: 'C',
      pillClass: 'party-pill-a',
      status: 'official',
      statusLabel: 'Programa oficial',
      isFixture: true
    },
    'party-d': {
      id: 'party-d',
      name: 'Partido D',
      shortName: 'Partido D',
      pill: 'D',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: true
    },
    // Aliases to match schema fixture IDs
    'partido-ejemplo-a': {
      id: 'partido-ejemplo-a',
      name: 'Partido Ejemplo A',
      shortName: 'Partido A',
      pill: 'A',
      pillClass: 'party-pill-a',
      status: 'official',
      statusLabel: 'Programa oficial',
      isFixture: true
    },
    'partido-ejemplo-b': {
      id: 'partido-ejemplo-b',
      name: 'Partido Ejemplo B',
      shortName: 'Partido B',
      pill: 'B',
      pillClass: 'party-pill-b',
      status: 'partial',
      statusLabel: 'Documento parcial',
      isFixture: true
    },
    'coalicion-ejemplo-c': {
      id: 'coalicion-ejemplo-c',
      name: 'Coalición Ejemplo C',
      shortName: 'Coalición C',
      pill: 'C',
      pillClass: 'party-pill-a',
      status: 'official',
      statusLabel: 'Programa oficial',
      isFixture: true
    },
    'partido-ejemplo-d': {
      id: 'partido-ejemplo-d',
      name: 'Partido Territorial Ejemplo D',
      shortName: 'Partido D',
      pill: 'D',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: true
    },
    // Official candidacies tracked for 2026
    'bng': {
      id: 'bng',
      name: 'Bloque Nacionalista Galego (BNG)',
      shortName: 'BNG',
      pill: 'BNG',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    },
    'ehbildu': {
      id: 'ehbildu',
      name: 'EH Bildu (Euskal Herria Bildu)',
      shortName: 'EH Bildu',
      pill: 'EHB',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    },
    'erc': {
      id: 'erc',
      name: 'Esquerra Republicana de Catalunya (ERC)',
      shortName: 'ERC',
      pill: 'ERC',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    },
    'junts': {
      id: 'junts',
      name: 'Junts per Catalunya',
      shortName: 'Junts',
      pill: 'JUN',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    },
    'pnv': {
      id: 'pnv',
      name: 'EAJ-PNV (Partido Nacionalista Vasco)',
      shortName: 'EAJ-PNV',
      pill: 'PNV',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    },
    'pp': {
      id: 'pp',
      name: 'Partido Popular (PP)',
      shortName: 'PP',
      pill: 'PP',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    },
    'psoe': {
      id: 'psoe',
      name: 'Partido Socialista Obrero Español (PSOE)',
      shortName: 'PSOE',
      pill: 'PSOE',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    },
    'sumar': {
      id: 'sumar',
      name: 'Movimiento Sumar',
      shortName: 'Sumar',
      pill: 'SUM',
      pillClass: 'party-pill-b',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    },
    'vox': {
      id: 'vox',
      name: 'VOX',
      shortName: 'VOX',
      pill: 'VOX',
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    }
  };

  // Measures grouped by topic, with positions, caveats, source citations, and pairwise relationships
  const MEASURES_BY_TOPIC = {
    'housing': [
      {
        id: 'housing-pilot-2023-measure',
        electionId: 'es-gen-2023',
        title: 'Medida: Regulación de precios de alquiler y acceso a la vivienda (2023)',
        summary: 'Propuestas de los programas electorales de las elecciones generales del 23 de julio de 2023 en materia de precios del alquiler, avales públicos y competencias autonómicas.',
        context: 'Esta iniciativa contrasta los modelos de política residencial ante el alza de precios: intervención directa del mercado del alquiler frente a estímulos y avales financieros para la compraventa, así como la delimitación competencial entre el Estado central y las comunidades autónomas con competencias forales o estatutarias.',
        keyAxes: [
          'Precios del alquiler: regulación vinculante (topes e índices obligatorios) frente a incentivos a la oferta y libre mercado.',
          'Acceso juvenil: avales públicos de hasta el 95% para compraventa frente a fomento de parque público de alquiler protegido.',
          'Régimen competencial: ley estatal homogénea frente a respeto exclusivo a competencias autonómicas y forales.'
        ],
        positions: {
          'pp': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Programa de avales para jóvenes de hasta 35 años destinado a facilitar créditos hipotecarios de hasta el 95% del precio de la vivienda y derogación de la Ley de Vivienda.',
            quote: 'LLEVAREMOS A CABO UN PROGRAMA DE AVALES DESTINADO A JÓVENES de hasta 35 años, a fin de garantizar la concesión de créditos hipotecarios por valor de hasta un 95% de la totalidad del precio de la vivienda.',
            policyInstrument: 'Programa de avales para préstamos hipotecarios de compraventa',
            section: 'Medida 91 · Página 34 (impresa 32)',
            qualifications: [
              'El 95% se refiere al importe del crédito respecto al precio de la vivienda, no al porcentaje del aval.',
              'Derogación de la Ley de Vivienda estatal de 2023.'
            ],
            source: 'Programa Electoral PP 23J · Medida 91, pág. 34 (impresa 32)',
            sourceUrl: 'https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf#page=34',
            date: '06/07/2023'
          },
          'erc': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Permitir que las comunidades autónomas con competencias en vivienda y derecho civil regulen íntegramente los contratos de arrendamiento urbano, incluidos los precios.',
            quote: 'Fer possible que les comunitats autònomes que tinguin competències en matèria d’habitatge i dret civil, foral o especial, puguin regular íntegrament els contractes d’arrendaments urbans, incloent la regulació dels preus de lloguer',
            policyInstrument: 'Habilitación competencial plena para regular precios de arrendamiento urbano',
            section: 'Habitatge, Sec. c · Página 114 (impresa 113)',
            qualifications: [
              'Propuesta limitada a comunidades autónomas con competencias en vivienda y derecho civil foral o especial.',
              'En el marco del art. 150.1 de la Constitución.'
            ],
            source: 'Programa Electoral 2023 · Sec. c, pág. 114 (impresa 113)',
            sourceUrl: 'https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf#page=114',
            date: '07/07/2023'
          },
          'sumar': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Modificación de la Ley de Vivienda para establecer regulación efectiva de precios del alquiler e inclusión de alquiler social obligatorio para grandes tenedores.',
            quote: 'Modificaremos la Ley 12/2023 de Vivienda para incluir: el alquiler social obligatorio para grandes tenedores, regulación efectiva de precios del alquiler y desarrollo de los índices de precios de referencia.',
            policyInstrument: 'Regulación obligatoria de precios del alquiler y alquiler social a grandes tenedores',
            section: 'Medida 14 · Página 77',
            qualifications: [
              'Aplicación obligatoria en zonas declaradas de mercado tensionado.',
              'Objetivo de constituir 2 millones de viviendas sociales y asequibles en diez años.'
            ],
            source: 'Un Programa para ti · Medida 14, pág. 77',
            sourceUrl: 'https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf#page=77',
            date: '06/07/2023'
          },
          'pnv': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Fomento del alquiler y promoción de vivienda pública suficiente respetando el marco competencial autonómico exclusivo y rechazando normas estatales invasivas.',
            quote: 'Abogamos por políticas que fomenten el alquiler y la promoción de vivienda pública suficiente para hacer frente a esta realidad, tal y como se viene desarrollando por el Gobierno Vasco dentro de su ámbito competencial exclusivo.',
            policyInstrument: 'Promoción de parque público de alquiler protegido bajo marco foral exclusivo',
            section: 'Punto 12 · Página 45',
            qualifications: [
              'Rechazo a leyes estatales que erosionen el autogobierno vasco en materia de vivienda.'
            ],
            source: 'Con voz propia · Punto 12, pág. 45',
            sourceUrl: 'https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j#page=45',
            date: '07/07/2023'
          }
        },
        relationships: {
          'pp:erc': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Divergencia entre avales hipotecarios para compra (PP) frente a habilitación autonómica para topar precios de alquiler (ERC).',
            differences: [
              'El PP propone facilitar crédito hipotecario de hasta el 95% para compraventa.',
              'ERC exige transferir competencias plenas para fijar topes al alquiler a nivel autonómico.'
            ]
          },
          'pp:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Divergencia entre avales hipotecarios para compraventa (PP) frente a regulación vinculante de precios de alquiler y alquiler social obligatorio (Sumar).',
            differences: [
              'El PP propone avales hipotecarios de hasta el 95% y derogar la Ley de Vivienda.',
              'Sumar propone índices de precios obligatorios y alquiler social para grandes tenedores.'
            ]
          },
          'pp:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Matiz en el instrumento prioritario: el PP enfatiza avales para compraventa, mientras el PNV centra su modelo en el parque público de alquiler protegido.',
            differences: [
              'El PP enfoca sus medidas en la compraventa avalada para menores de 35 años.',
              'El PNV prioriza el alquiler público gestionado bajo competencias forales exclusivas.'
            ]
          },
          'erc:sumar': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Coincidencia en regular y topar los precios del alquiler residencial, con matices en el ámbito competencial de aplicación.',
            differences: [
              'Sumar defiende una regulación estatal homogénea con índices vinculantes.',
              'ERC reclama transferir la competencia regulatoria plena a las comunidades autónomas.'
            ]
          },
          'pnv:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en priorizar el alquiler público y protegido, con discrepancia en el grado de centralización normativa.',
            differences: [
              'Sumar promueve una reforma vinculante estatal de la Ley de Vivienda.',
              'El PNV rechaza la invasión del marco competencial autonómico vasco.'
            ]
          },
          'erc:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en la defensa del marco competencial autonómico, con distinto énfasis en la intervención directa de precios.',
            differences: [
              'ERC reclama transferir competencias para topar directamente los precios de los contratos.',
              'El PNV prioriza la gestión de alquiler protegido autonómico sin centrarse en topes de precios.'
            ]
          }
        }
      },
      {
        id: 'housing-rental-regulation',
        title: 'Medida: Regulación de precios de alquiler en zonas de mercado tensionado',
        summary: 'Políticas de contención y límites obligatorios a los precios de arrendamiento de vivienda en áreas declaradas de mercado tensionado.',
        context: 'Esta medida evalúa las políticas de contención del alquiler residencial frente al incremento de precios en áreas urbanas, analizando los modelos de índice de precios de referencia y el régimen sancionador a grandes tenedores.',
        keyAxes: [
          'Modelo de contención: índice estatal homogéneo vinculante frente a índices de ajuste autonómico.',
          'Régimen de excepciones: moratorias temporales por rehabilitación integral frente a aplicación general sin exenciones.'
        ],
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Limitar los precios de alquiler en zonas tensionadas mediante un índice estatal de referencia y sanciones a grandes tenedores infractores.',
            quote: 'Estableceremos un límite de precios vinculante en zonas de mercado residencial tensionado basado en el índice de precios de referencia.',
            policyInstrument: 'Índice estatal vinculante de precios de referencia',
            section: 'Página 34',
            qualifications: [
              'Aplica exclusivamente en municipios declarados como zona de mercado tensionado.',
              'Exención temporal de dos años para viviendas objeto de rehabilitación energética integral.'
            ],
            source: 'Programa de ejemplo v1.0 · pág. 34',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=34',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Intervenir los precios del alquiler en áreas tensionadas mediante índices autonómicos y movilización de viviendas desocupadas.',
            quote: 'Toparemos los precios abusivos del alquiler en las zonas residenciales declaradas tensionadas.',
            policyInstrument: 'Índices autonómicos de precios y movilización de vivienda desocupada',
            section: 'Página 8',
            qualifications: [
              'Prevé competencia transferida a las comunidades autónomas para ajustar los índices a la baja.'
            ],
            source: 'Manifiesto parcial v0.9 · pág. 8',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=8',
            date: '16/10/2026'
          },
          'party-d': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'No se localiza propuesta ni posición sobre regulación de precios de alquiler en las fuentes oficiales revisadas de esta candidatura.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Registro oficial de fuentes (src-2026-fixture-d-v0)',
            sourceUrl: null,
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Ambas formaciones políticas proponen establecer techos vinculantes de precios para alquileres de vivienda en áreas declaradas de mercado tensionado.',
            differences: [
              'Partido A condiciona la medida a un índice estatal único; Partido B prevé que las comunidades autónomas puedan fijar índices más restrictivos.',
              'Partido A introduce una exención de 2 años por rehabilitación integral; Partido B no contempla exenciones temporales.'
            ]
          },
          'party-a:party-d': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido A propone regulación vinculante de precios, mientras que en las fuentes oficiales de Partido D no consta propuesta sobre la materia.',
            differences: [
              'Partido D tiene estado «no consta» en su programa; la ausencia documental no constituye oposición política.'
            ]
          }
        }
      },
      {
        id: 'housing-youth-subsidy',
        title: 'Medida: Ayudas públicas directas y avales para acceso a la vivienda para jóvenes',
        summary: 'Instrumentos de apoyo financiero público para facilitar la emancipación y la adquisición o fianza de primera vivienda por jóvenes menores de 35 años.',
        context: 'Esta medida analiza las fórmulas de intervención pública para facilitar el acceso de jóvenes a la vivienda habitual, contrastando subvenciones directas a intereses frente a coberturas crediticias de fianza o entrada.',
        keyAxes: [
          'Instrumento financiero: bonificación de tipos de interés hipotecario frente a líneas directas de aval de entrada.',
          'Criterios de elegibilidad: límites de renta basados en múltiplos del IPREM (3,5x frente a 4x).'
        ],
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Bonificación pública de tipos de interés hipotecarios para adquisición de primera vivienda por jóvenes menores de 35 años con renta inferior a 3,5 veces el IPREM.',
            quote: 'Bonificaremos hasta dos puntos el tipo de interés de las hipotecas para jóvenes menores de 35 años que compren su primera vivienda.',
            policyInstrument: 'Bonificación de tipos de interés hipotecario para menores de 35 años',
            section: 'Página 38',
            qualifications: [
              'Límite de renta individual o de unidad de convivencia fijado en 3,5 veces el IPREM.',
              'Aplica exclusivamente para hipotecas sobre vivienda habitual.'
            ],
            source: 'Programa de ejemplo v1.0 · pág. 38',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=38',
            date: '16/10/2026'
          },
          'coalicion-c': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Línea de avales públicos directos del Estado de hasta el 20% del valor de tasación para la fianza o entrada hipotecaria de menores de 35 años con renta hasta 4 veces el IPREM.',
            quote: 'Habilitaremos un aval público del 20% para la compra de primera vivienda por personas jóvenes con ingresos de hasta cuatro veces el IPREM.',
            policyInstrument: 'Línea de avales públicos del 20% del valor de tasación',
            section: 'Página 52',
            qualifications: [
              'Límite de ingresos de 4 veces el IPREM.',
              'Compatible con ayudas autonómicas de emancipación juvenil.'
            ],
            source: 'Programa de ejemplo v2.0 · pág. 52',
            sourceUrl: 'https://coalicion-ejemplo-c.es/programa-v2.pdf#page=52',
            date: '17/10/2026'
          },
          'party-b': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'El programa revisado no incluye una propuesta explícita sobre esta medida concreta.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Manifiesto parcial v0.9',
            sourceUrl: null,
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:coalicion-c': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '~',
            summary: 'Ambas candidaturas contemplan apoyo público al acceso a la vivienda para menores de 35 años, pero mediante instrumentos operativos distintos.',
            differences: [
              'Instrumento principal: subvención al tipo de interés (Partido A) frente a aval estatal de entrada hipotecaria (Coalición C).',
              'Umbral de renta: Partido A limita a 3,5 veces el IPREM; Coalición C limita a 4 veces el IPREM.'
            ]
          },
          'party-a:party-b': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido A propone bonificación de tipos de interés hipotecarios, mientras que en el documento revisado de Partido B no consta propuesta específica sobre este instrumento.',
            differences: [
              '«No consta» indica ausencia documental en el texto; nunca se interpretará como oposición política.'
            ]
          }
        }
      },

    ],

    'economy-work-tax': [
      {
        id: 'economy-pilot-2023-measure',
        electionId: 'es-gen-2023',
        title: 'Medida: Regulación de la jornada laboral máxima y tiempo de trabajo (2023)',
        summary: 'Propuestas de los programas electorales de las elecciones generales del 23 de julio de 2023 sobre la duración máxima legal de la jornada laboral, reducciones horarias y el marco de la negociación colectiva.',
        context: 'Esta iniciativa aborda el debate sobre la reducción del tiempo de trabajo semanal sin merma salarial frente a la flexibilidad horaria adaptada a la productividad empresarial, contrastando una regulación legal vinculante frente al marco de convenios y diálogo social territorial.',
        keyAxes: [
          'Duración legal: reducción por ley a 37,5 h (con proceso hacia las 32 h o cuatro días) frente a mantenimiento de la jornada máxima legal con flexibilidad pactada.',
          'Compensación salarial: reducción de jornada garantizando el 100% de la retribución salarial sin merma económica.',
          'Marco competencial: regulación uniforme en el Estatuto de los Trabajadores frente a traspaso de la competencia laboral o primacía de convenios autonómicos.'
        ],
        positions: {
          'sumar': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Fijar por ley en 2024 una jornada laboral máxima de 37,5 horas semanales sin reducción de salario, y abrir diálogo social para avanzar hacia las 32 horas.',
            quote: 'En 2024 se establecerá por ley una jornada laboral máxima de 37,5 horas y se abrirá un proceso de diálogo social para seguir reduciendo la jornada hasta alcanzar las 32 horas semanales.',
            policyInstrument: 'Modificación del Estatuto de los Trabajadores para fijar jornada máxima en 37,5 h',
            section: 'Punto 4 · Página 24',
            qualifications: [
              'Sin reducción de salario.',
              'Apertura de proceso de diálogo social para reducción progresiva hasta 32 horas.'
            ],
            source: 'Un Programa para ti · Punto 4, pág. 24',
            sourceUrl: 'https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf#page=24',
            date: '06/07/2023'
          },
          'pp': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Rechazo a la reducción legal obligatoria de jornada; fomento de la flexibilidad horaria en convenios y actualización del SMI mediante diálogo social.',
            quote: 'ACTUALIZAREMOS EL SALARIO MÍNIMO INTERPROFESIONAL EN EL MARCO DEL DIÁLOGO SOCIAL. Involucraremos a sindicatos, empresarios y expertos en la toma de decisiones sobre el SMI.',
            policyInstrument: 'Flexibilidad pactada en negociación colectiva y actualización del SMI en diálogo social',
            section: 'Medida 22 · Página 19 (impresa 17)',
            qualifications: [
              'No propone reducción obligatoria de la jornada máxima legal en el texto del programa.',
              'Prioriza medidas de fomento de productividad y flexibilidad horaria pactada.'
            ],
            source: 'Programa Electoral PP 23J · Medida 22, pág. 19 (impresa 17)',
            sourceUrl: 'https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf#page=19',
            date: '06/07/2023'
          },
          'erc': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Implementar la jornada laboral de cuatro días sin pérdida salarial y exigir el traspaso íntegro de la legislación laboral a la Generalitat.',
            quote: 'protegeixi les classes treballadores davant els abusos del mercat, que recuperi instruments com els salaris de tramitació o l’autorització administrativa dels ERO, en reforci d’altres com la indemnització per acomiadament i implementi mesures com la jornada laboral de quatre dies.',
            policyInstrument: 'Jornada laboral de 4 días y traspaso de la competencia laboral',
            section: 'Defensa de la classe treballadora · Página 53 (impresa 52)',
            qualifications: [
              'Reivindica marco catalán de relaciones laborales y traspaso de competencias.'
            ],
            source: 'Programa Electoral 2023 · pág. 53 (impresa 52)',
            sourceUrl: 'https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf#page=53',
            date: '07/07/2023'
          },
          'pnv': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Respetar el marco vasco de relaciones laborales y acuerdos en diálogo social para adaptar los tiempos de trabajo sin imposiciones estatales.',
            quote: 'Entendemos necesario abordar el debate sobre el empleo del futuro, que deberá seguir estando residenciado en el diálogo social y, por ello, en un modelo de relaciones laborales sustentado en el equilibrio de poder entre trabajadores y trabajadoras y empresarios',
            policyInstrument: 'Defensa del marco vasco de relaciones laborales y negociación colectiva propia',
            section: 'El empleo, nuevos retos · Página 29 (impresa 29)',
            qualifications: [
              'Supeditado a acuerdos en mesas de diálogo social.',
              'Rechaza cualquier recentralización de la negociación colectiva autonómica.'
            ],
            source: 'Con voz propia · Punto 8, pág. 29',
            sourceUrl: 'https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j#page=29',
            date: '07/07/2023'
          }
        },
        relationships: {
          'pp:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre reducción legal obligatoria a 37,5 horas (Sumar) frente a flexibilidad horaria pactada en convenios sin reducciones legales uniformes (PP).',
            differences: [
              'Sumar propone fijar por ley una jornada máxima de 37,5 horas en 2024 sin merma salarial.',
              'El PP defiende la flexibilidad y adaptación acordada en negociación colectiva sin topes legales reducidos.'
            ]
          },
          'pp:erc': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre jornada laboral de cuatro días (ERC) frente al modelo de flexibilidad pactada y diálogo social para el SMI (PP).',
            differences: [
              'ERC propone implantar la jornada de cuatro días y traspasar la legislación laboral a la Generalitat.',
              'El PP centra sus medidas en productividad y actualización pactada del SMI sin alterar la jornada legal.'
            ]
          },
          'pp:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en remitir las condiciones laborales a la negociación colectiva y el diálogo social, con énfasis del PNV en el marco vasco propio.',
            differences: [
              'El PP prioriza la productividad empresarial y la unidad de mercado laboral estatal.',
              'El PNV demanda blindar el marco vasco de relaciones laborales y el diálogo social autónomo.'
            ]
          },
          'erc:sumar': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Coincidencia en reducir el tiempo de trabajo sin merma salarial hacia las 32 horas o cuatro días, con matiz competencial.',
            differences: [
              'Sumar promueve una reforma legal estatal uniforme en el Estatuto de los Trabajadores.',
              'ERC reivindica que la competencia sobre relaciones laborales sea traspasada a las instituciones catalanas.'
            ]
          },
          'erc:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en la defensa del marco autonómico de relaciones laborales, con mayor énfasis de ERC en fijar la jornada de 4 días.',
            differences: [
              'ERC defiende como objetivo programático explícito la jornada de cuatro días.',
              'El PNV supedita las adaptaciones a los acuerdos entre patronal y sindicatos en el diálogo social vasco.'
            ]
          },
          'pnv:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en mejorar las condiciones laborales, con discrepancia en el carácter vinculante de una ley estatal frente a los convenios autonómicos.',
            differences: [
              'Sumar aboga por una ley estatal de 37,5 horas de obligado cumplimiento en todo el territorio.',
              'El PNV defiende la autonomía de los convenios y la prevalencia de los marcos vascos de negociación.'
            ]
          }
        }
      },
      {
        id: 'economy-smi',
        title: 'Medida: Evolución y fijación del Salario Mínimo Interprofesional (SMI)',
        summary: 'Criterios legales para la fijación del SMI y su adecuación al coste de la vida y al salario medio.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Blindar por ley que el Salario Mínimo Interprofesional alcance de forma permanente el 60% del salario medio neto en España.',
            quote: 'Blindaremos en el Estatuto de los Trabajadores que el Salario Mínimo Interprofesional equivalga al 60% del salario medio neto.',
            qualifications: [
              'Revisión anual vinculada a los datos del Comité de Expertos del Ministerio de Trabajo.'
            ],
            source: 'Programa de ejemplo v1.0 · pág. 19',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=19',
            date: '16/10/2026'
          },
          'party-d': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'No se localiza propuesta ni posición sobre fijación del salario mínimo en las fuentes oficiales revisadas de esta candidatura.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Registro oficial de fuentes (src-2026-fixture-d-v0)',
            sourceUrl: null,
            date: '17/10/2026'
          }
        },
        relationships: {
          'party-a:party-d': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido A propone blindar el SMI al 60% del salario medio neto, mientras que Partido D no dispone de programa ni posición localizada sobre la materia.',
            differences: [
              'Partido D tiene estado «no consta» en su programa para 2026; la ausencia no constituye oposición.'
            ]
          }
        }
      },
      {
        id: 'economy-working-hours',
        title: 'Medida: Regulación de la jornada laboral máxima legal y diálogo social',
        summary: 'Modificación de la jornada semanal ordinaria de trabajo y plazos transitorios de adaptación sectorial.',
        positions: {
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Reducir la jornada laboral máxima legal a 37,5 horas semanales sin reducción de salario, con calendario de adaptación sectorial.',
            quote: 'Avanzaremos hacia la jornada laboral de 37,5 horas semanales sin merma salarial mediante diálogo social.',
            qualifications: [
              'Sujeto a acuerdos en mesas de diálogo social tripartito.',
              'Período transitorio de dos años para pequeñas y medianas empresas con menos de 10 trabajadores.'
            ],
            source: 'Manifiesto parcial v0.9 · pág. 12',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=12',
            date: '17/10/2026'
          },
          'party-a': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'El programa revisado no incluye una propuesta explícita sobre reducción horaria de jornada máxima.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Programa de ejemplo v1.0',
            sourceUrl: null,
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido B propone reducción legal a 37,5 horas semanales, mientras que en el texto de Partido A no figura propuesta específica en esta materia.',
            differences: [
              '«No consta» indica ausencia documental en el texto; nunca se interpretará como oposición política.'
            ]
          }
        }
      }
    ],

    'education': [
      {
        id: 'education-pilot-2023-measure',
        electionId: 'es-gen-2023',
        title: 'Medida: Gratuidad y universalización de la educación infantil de 0 a 3 años (2023)',
        summary: 'Propuestas de los programas electorales del 23J de 2023 relativas a la gratuidad y universalización del primer ciclo de educación infantil (0 a 3 años) y su modelo de financiación.',
        context: 'Esta iniciativa contrasta las propuestas para garantizar el acceso universal y gratuito a la educación infantil de 0 a 3 años: fórmulas de cofinanciación estatal y autonómica con inclusión del sector concertado y privado frente a la creación prioritaria o exclusiva de plazas públicas y la defensa del marco competencial autonómico.',
        keyAxes: [
          'Alcance de la gratuidad: acceso universal y gratuito al primer ciclo de educación infantil (0 a 3 años).',
          'Modelo de provisión: plazas públicas exclusivas frente a modelos de colaboración y concierto con el sector privado cofinanciados al 50% con las CC. AA.',
          'Marco competencial: financiación estatal respetando las competencias autonómicas frente a planes estatales coordinados.'
        ],
        positions: {
          'pp': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Universalidad y gratuidad de la educación de 0 a 3 años cofinanciada al 50% entre el Gobierno y las comunidades autónomas, promoviendo la colaboración público-privada.',
            quote: 'LA EDUCACIÓN DE 0-3 SERÁ UNIVERSAL Y GRATUITA y estará cofinanciada por el Gobierno de España y las Comunidades Autónomas al 50%. Promoveremos la colaboración con el sector público y privado.',
            policyInstrument: 'Cofinanciación al 50% con CC. AA. y colaboración público-privada para gratuidad de 0 a 3 años',
            section: 'Medida 164 · Página 53 (impresa 51)',
            qualifications: [
              'Cofinanciación al 50% entre el Gobierno central y las comunidades autónomas.',
              'Apertura explícita a la colaboración con el sector privado.'
            ],
            source: 'Programa Electoral PP 23J · Medida 164, pág. 53 (impresa 51)',
            sourceUrl: 'https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf#page=53',
            date: '06/07/2023'
          },
          'sumar': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Acceso universal y gratuito a la educación infantil de 0 a 3 años mediante oferta de servicios públicos.',
            quote: 'Educación infantil de 0 a 3 años. La oferta de los servicios públicos de educación infantil de 0 a 3 años será de acceso universal y gratuito.',
            policyInstrument: 'Universalización y gratuidad a través de la red de servicios públicos',
            section: 'Punto 3 · Página 94',
            qualifications: [
              'Enfocado en la red de plazas y servicios públicos.'
            ],
            source: 'Un Programa para ti · Punto 3, pág. 94',
            sourceUrl: 'https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf#page=94',
            date: '06/07/2023'
          },
          'erc': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Garantizar financiación estatal estable para la creación de plazas públicas y universalizar el primer ciclo de educación infantil de 0 a 3 años.',
            quote: 'Garantir el finançament adequat i estable per part de l\'Estat per a la creació de places públiques amb l\'objectiu d\'universalitzar el primer cicle d\'educació infantil 0-3 anys.',
            policyInstrument: 'Financiación estatal para plazas públicas del primer ciclo de educación infantil',
            section: 'Educació · Página 128 (impresa 127)',
            qualifications: [
              'Exige dotación y transferencias financieras del Estado respetando las competencias de la Generalitat.'
            ],
            source: 'Programa Electoral 2023 · Educació, pág. 128 (impresa 127)',
            sourceUrl: 'https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf#page=128',
            date: '07/07/2023'
          },
          'pnv': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Defensa del marco competencial autonómico exclusivo en educación para desarrollar el modelo propio de acceso y oportunidades de 0 a 3 años.',
            quote: 'nos comprometemos a seguir trabajando para que se respete el régimen de distribución competencial vigente en el ámbito educativo. Que podamos seguir desarrollando nuestro propio modelo educativo.',
            policyInstrument: 'Defensa competencial y autogobierno educativo vasco',
            section: 'Punto 13 · Página 48 (impresa 48)',
            qualifications: [
              'Prioriza la no invasión competencial estatal en las políticas educativas del Gobierno Vasco.'
            ],
            source: 'Con voz propia · Punto 13, pág. 48',
            sourceUrl: 'https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j#page=48',
            date: '07/07/2023'
          }
        },
        relationships: {
          'pp:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en la gratuidad y universalidad de la educación 0-3 años, con discrepancia en la inclusión del sector privado y la financiación.',
            differences: [
              'El PP propone cofinanciación al 50% con CC. AA. y colaboración con el sector privado.',
              'Sumar centra la gratuidad y universalidad en la red de servicios públicos exclusivamente.'
            ]
          },
          'pp:erc': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en el objetivo de universalizar la etapa 0-3 años, pero con diferencias en el modelo de provisión y competencias.',
            differences: [
              'El PP incluye colaboración con el sector privado y esquema de cofinanciación bipartito al 50%.',
              'ERC exige financiación estatal exclusiva para la creación de plazas públicas gestionadas por la Generalitat.'
            ]
          },
          'pp:pnv': {
            type: 'divergence',
            typeLabel: 'Discrepancia competencial',
            icon: '≠',
            summary: 'Discrepancia en el marco institucional: plan cofinanciado estatal del PP frente a exigencia del PNV de no injerencia en las competencias educativas vascas.',
            differences: [
              'El PP diseña un marco común de cofinanciación y gratuidad estatal.',
              'El PNV rechaza condiciones estatales que interfieran en el despliegue del modelo educativo propio vasco.'
            ]
          },
          'erc:sumar': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Coincidencia en la universalización y gratuidad de la etapa 0-3 años basada en plazas y servicios de la red pública.',
            differences: [
              'ERC pone el foco en la transferencia y financiación estable del Estado hacia las administraciones autonómicas.',
              'Sumar plantea la universalización como mandato y cobertura general del sistema educativo público.'
            ]
          },
          'erc:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en la reivindicación competencial y financiación estatal, con diferente nivel de concreción en la medida 0-3.',
            differences: [
              'ERC plantea explícitamente financiación estatal para crear plazas públicas de 0-3 años.',
              'El PNV defiende de forma transversal el blindaje competencial educativo de las instituciones vascas.'
            ]
          },
          'pnv:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia competencial',
            icon: '≠',
            summary: 'Discrepancia entre la definición estatal de la oferta pública gratuita (Sumar) y la exigencia de respeto competencial autonómico (PNV).',
            differences: [
              'Sumar propone un mandato estatal general de acceso universal público de 0 a 3 años.',
              'El PNV subordina cualquier iniciativa al respeto escrupuloso de las competencias de la comunidad autónoma.'
            ]
          }
        }
      },
      {
        id: 'education-funding-ratios',
        title: 'Medida: Financiación de centros públicos y conciertos educativos',
        summary: 'Criterios de asignación presupuestaria a la red escolar pública y régimen de conciertos educativos.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Incrementar el gasto público educativo hasta el 5,5% del PIB con prioridad en infraestructuras y profesorado de la red pública.',
            qualifications: ['Condicionado a techos de gasto y convenios de cofinanciación con comunidades autónomas.'],
            source: 'Programa de ejemplo v1.0 · pág. 48',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=48',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Mantenimiento del régimen de conciertos educativos garantizando gratuidad real y libertad de elección de centro.',
            qualifications: ['Sujeto a auditorías de costes reales por puesto escolar.'],
            source: 'Manifiesto parcial v0.9 · pág. 16',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=16',
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'divergence',
            typeLabel: 'Diferencia en instrumento o alcance',
            icon: '↔',
            summary: 'Partido A prioriza la inversión exclusiva en la red pública, mientras que Partido B defiende consolidar el modelo de conciertos educativos.',
            differences: [
              'Destino de los fondos: exclusividad de la red pública frente a sostenimiento del régimen concertado.'
            ]
          }
        }
      },
      {
        id: 'education-classroom-ratios',
        title: 'Medida: Ratios de alumnado por aula y recursos de inclusión escolar',
        summary: 'Límites máximos de estudiantes por docente y dotación de personal de orientación y necesidades educativas especiales.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Reducción progresiva de las ratios máximas a 20 alumnos en educación primaria y 25 en educación secundaria obligatoria.',
            qualifications: ['Aplicación escalonada a lo largo de una legislatura completa.'],
            source: 'Programa de ejemplo v1.0 · pág. 50',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=50',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'El programa revisado no incluye una cifra explícita sobre ratios máximas por aula.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Manifiesto parcial v0.9',
            sourceUrl: null,
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido A formula una meta cuantitativa de reducción de ratios, mientras que en el documento de Partido B no consta propuesta específica.',
            differences: ['«No consta» no implica oposición política.']
          }
        }
      }
    ],

    'health-social-services': [
      {
        id: 'health-pilot-2023-measure',
        electionId: 'es-gen-2023',
        title: 'Medida: Refuerzo de la Atención Primaria y Salud Mental en el SNS (2023)',
        summary: 'Propuestas de los programas electorales del 23J de 2023 sobre el refuerzo de la atención primaria, contratación de profesionales médicos y estrategias de salud mental.',
        context: 'Esta iniciativa contrasta las estrategias ante la saturación de la atención primaria y las listas de espera: planes de choque estatales y ampliación de plazas MIR frente a planes integrales de salud mental y la transferencia plena de la formación sanitaria especializada a las comunidades autónomas.',
        keyAxes: [
          'Atención primaria y déficit médico: planes de choque de fidelización y cambios en el sistema MIR frente a transferencias competenciales de gestión formativa.',
          'Salud mental: estrategias nacionales de detección temprana frente a planes comunitarios con enfoque interdisciplinar y determinantes sociales.',
          'Modelo organizativo: coordinación y financiación estatal frente al traspaso íntegro de la gestión de Formación Sanitaria Especializada (FSE).'
        ],
        positions: {
          'pp': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Plan de choque en atención primaria para paliar el déficit de médicos de familia y pediatras, y nueva Estrategia Nacional en Salud Mental centrada en la infancia.',
            quote: 'PROMOVEREMOS UN PLAN DE CHOQUE EN ATENCIÓN PRIMARIA para dar respuesta urgente a la falta de médicos de familia y pediatras (...) aprobando una nueva Estrategia Nacional en Salud Mental, centrada en la atención temprana',
            policyInstrument: 'Plan de choque de recursos humanos en primaria y Estrategia Nacional en Salud Mental',
            section: 'Medidas 120 y 134 · Páginas 45 y 49 (impresas 43 y 47)',
            qualifications: [
              'Reforma de la jubilación activa de médicos de familia y pediatras hasta los 72 años.',
              'Nueva Estrategia Nacional en Salud Mental focalizada en la atención temprana.'
            ],
            source: 'Programa Electoral PP 23J · Medidas 120 y 134, págs. 45 y 49 (impresas 43 y 47)',
            sourceUrl: 'https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf#page=45',
            date: '06/07/2023'
          },
          'sumar': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Plan de choque en salud mental sensible a determinantes sociales y refuerzo estructural de la atención primaria dotándola de mayor presupuesto.',
            quote: 'Pondremos en marcha un Plan de Choque en Salud Mental que aborde los problemas de forma interdisciplinar y sensible a los determinantes sociales (...) vertebrada desde la atención primaria y comunitaria.',
            policyInstrument: 'Plan de Choque interdisciplinar en Salud Mental y fortalecimiento de la atención primaria comunitaria',
            section: 'Punto 7 · Página 90',
            qualifications: [
              'Aborda los problemas desde los determinantes sociales y la perspectiva comunitaria.',
              'Incremento del gasto sanitario público destinado a atención primaria.'
            ],
            source: 'Un Programa para ti · Punto 7, pág. 90',
            sourceUrl: 'https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf#page=90',
            date: '06/07/2023'
          },
          'erc': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Transferencia financiera estatal para planes de salud bucodental y participación en la gestión y plazas de la Formación Sanitaria Especializada (FSE).',
            quote: 'Transferència financera per a l’aplicació efectiva dels plans de salut bucodental inclosos a la cartera de serveis (...) participació en la prova d’accés a la Formació Sanitària Especialitzada (FSE) pel que fa al seu desenvolupament, gestió i avaluació.',
            policyInstrument: 'Transferencias financieras para salud bucodental y codecisión en la gestión de la FSE',
            section: 'Salut · Página 62 (impresa 61)',
            qualifications: [
              'Demanda codecisión y gestión autonómica en el acceso y evaluación del MIR/FSE.',
              'Financiación estatal directa sin condicionamientos centralizados.'
            ],
            source: 'Programa Electoral 2023 · Salut, pág. 62 (impresa 61)',
            sourceUrl: 'https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf#page=62',
            date: '07/07/2023'
          },
          'pnv': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Transferencia inmediata de la competencia de Formación Sanitaria Especializada y adecuación urgente de plazas del MIR para evitar vacantes.',
            quote: 'Transferencia de las competencias pendientes: formación sanitaria especializada, acreditación de plazas, control sanitario de incapacidades laborales (...) cambios en el MIR de manera que se adecúen las plazas y que no queden vacantes',
            policyInstrument: 'Transferencia plena de la Formación Sanitaria Especializada y reforma del sistema MIR',
            section: 'Punto 12 · Página 46 (impresa 46)',
            qualifications: [
              'Exige traspaso íntegro al Gobierno Vasco de la acreditación de plazas y gestión formativa.',
              'Reforma del procedimiento de adjudicación de plazas MIR para impedir plazas desiertas.'
            ],
            source: 'Con voz propia · Punto 12, pág. 46 (impresa 46)',
            sourceUrl: 'https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j#page=46',
            date: '07/07/2023'
          }
        },
        relationships: {
          'pp:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en priorizar la atención primaria y la salud mental, pero con distinto enfoque asistencial y organizativo.',
            differences: [
              'El PP plantea incentivos profesionales y prolongación voluntaria de jubilación médica hasta los 72 años.',
              'Sumar enfatiza el abordaje interdisciplinar, comunitario y centrado en los determinantes sociales del malestar.'
            ]
          },
          'pp:erc': {
            type: 'divergence',
            typeLabel: 'Discrepancia competencial',
            icon: '≠',
            summary: 'Discrepancia entre la gestión estatal centralizada de la atención primaria y MIR (PP) frente a la exigencia de traspaso de la FSE a Cataluña (ERC).',
            differences: [
              'El PP propone un plan de choque estatal único coordinado desde el Ministerio de Sanidad.',
              'ERC demanda transferencias financieras y participación directa en la gestión y examen de la Formación Sanitaria Especializada.'
            ]
          },
          'pp:pnv': {
            type: 'divergence',
            typeLabel: 'Discrepancia competencial',
            icon: '≠',
            summary: 'Discrepancia sobre la gobernanza formativa sanitaria: plan estatal de recursos humanos (PP) frente a transferencia íntegra de la FSE a Euskadi (PNV).',
            differences: [
              'El PP defiende un marco común de plazas y convocatoria MIR estatal.',
              'El PNV exige la transferencia pendiente de la Formación Sanitaria Especializada y la acreditación de plazas al País Vasco.'
            ]
          },
          'erc:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en ampliar coberturas del SNS (bucodental y salud mental), con matiz sobre la titularidad del gasto y competencias.',
            differences: [
              'ERC supedita las mejoras a la transferencia de fondos estatales para gestionarlos autonómicamente.',
              'Sumar promueve una ampliación general de coberturas y un plan de choque estatal vertebrado desde la atención primaria.'
            ]
          },
          'erc:pnv': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Coincidencia en reclamar la descentralización de la gestión sanitaria, en particular la Formación Sanitaria Especializada y el MIR.',
            differences: [
              'ERC resalta la transferencia de fondos bucodentales y evaluación compartida.',
              'El PNV exige la transferencia estatutaria completa de la FSE y cambios urgentes en el sistema de adjudicación MIR.'
            ]
          },
          'pnv:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia competencial',
            icon: '≠',
            summary: 'Discrepancia entre la articulación estatal comunitaria de la salud (Sumar) y la reivindicación de transferencia plena de competencias sanitarias (PNV).',
            differences: [
              'Sumar plantea directrices y planes de choque homogéneos en todo el Estado.',
              'El PNV insiste en que las decisiones organizativas y la gestión de formación médica corresponden al ámbito foral y autonómico.'
            ]
          }
        }
      },
      {
        id: 'health-primary-care',
        title: 'Medida: Refuerzo de la atención primaria y reducción de listas de espera',
        summary: 'Inversión en el Sistema Nacional de Salud, dotación de personal y cobertura de salud mental.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Destinar al menos el 25% del presupuesto sanitario autonómico a la atención primaria con ley de tiempos máximos de espera.',
            qualifications: ['Requiere acuerdo en el Consejo Interterritorial del SNS.'],
            source: 'Programa de ejemplo v1.0 · pág. 55',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=55',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Plan de choque para derivación concertada y reducción de demoras quirúrgicas en un plazo de doce meses.',
            qualifications: ['Actuación extraordinaria de vigencia temporal acotada.'],
            source: 'Manifiesto parcial v0.9 · pág. 20',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=20',
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'divergence',
            typeLabel: 'Diferencia en instrumento o alcance',
            icon: '↔',
            summary: 'Partido A propone blindaje presupuestario directo en atención primaria; Partido B plantea convenios temporales de colaboración con el sector privado.',
            differences: [
              'Instrumento: ampliación de plantilla estructural frente a derivación asistencial a centros concertados.'
            ]
          }
        }
      },
      {
        id: 'health-mental-health',
        title: 'Medida: Estrategia de salud mental y ampliación de cartera de servicios',
        summary: 'Incorporación de profesionales de psicología clínica y cobertura bucodental en el Sistema Nacional de Salud.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Garantizar un ratio de 18 psicólogos clínicos por cada 100.000 habitantes en centros de salud de atención primaria.',
            qualifications: ['Despliegue condicionado a la oferta de plazas PIR en la convocatoria anual.'],
            source: 'Programa de ejemplo v1.0 · pág. 58',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=58',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Ampliación progresiva del plan nacional de prevención del suicidio y unidades de atención infantojuvenil.',
            qualifications: ['Dotación presupuestaria sujeta a aprobación en Presupuestos Generales.'],
            source: 'Manifiesto parcial v0.9 · pág. 22',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=22',
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '~',
            summary: 'Ambas candidaturas coinciden en priorizar la salud mental, si bien con diferente nivel de concreción en ratios de profesionales.',
            differences: [
              'Partido A fija un umbral numérico de psicólogos en primaria; Partido B enfatiza programas de prevención y salud infantojuvenil.'
            ]
          }
        }
      }
    ],

    'immigration': [
      {
        id: 'immigration-pilot-2023-measure',
        electionId: 'es-gen-2023',
        title: 'Medida: Gestión de flujos migratorios, vías de regularización y acogida (2023)',
        summary: 'Propuestas de los programas electorales del 23J de 2023 sobre control de fronteras, regularización de personas migrantes, cierre de CIEs y distribución competencial de la acogida.',
        context: 'Esta iniciativa contrasta las políticas migratorias: refuerzo de inspección fronteriza y coordinación policial con FRONTEX frente a regularización permanente de derechos, cierre de los CIEs y traspaso de competencias de acogida a las comunidades autónomas.',
        keyAxes: [
          'Control fronterizo y seguridad: incremento de medios y refuerzo de FRONTEX frente a fin de devoluciones en caliente y vías legales seguras de entrada.',
          'Régimen de regularización: control estricto de entradas irregulares frente a reforma de la ley de extranjería y regularización permanente de derechos.',
          'Gobernanza de la acogida: gestión estatal y convenios bilaterales en origen frente a transferencia plena de políticas migratorias a las CC. AA.'
        ],
        positions: {
          'pp': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Refuerzo de la inspección fronteriza con medios policiales y tecnológicos, participación en FRONTEX y cooperación migratoria con países de origen.',
            quote: 'POTENCIAREMOS LA INSPECCIÓN FRONTERIZA, incrementando el número y formación del personal, impulsando la implantación del nuevo Sistema Europeo de Registro de Entradas y Salidas (...) y participación en las actividades de FRONTEX.',
            policyInstrument: 'Inspección de fronteras, coordinación con FRONTEX y acuerdos de retorno en origen',
            section: 'Medida 276 · Página 81 (impresa 79)',
            qualifications: [
              'Refuerzo de la Autoridad Nacional de Coordinación para la inmigración irregular.',
              'Equipos conjuntos de investigación con países africanos de origen y tránsito.'
            ],
            source: 'Programa Electoral PP 23J · Medida 276, pág. 81 (impresa 79)',
            sourceUrl: 'https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf#page=81',
            date: '06/07/2023'
          },
          'sumar': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Reforma de la ley de extranjería para regularización permanente de derechos, cierre de los CIEs y eliminación de barreras en sanidad pública.',
            quote: 'Reforma de la Ley Orgánica sobre Derechos y Libertades de los Extranjeros en España y su Integración Social (LOEX) que prime los criterios de reconocimiento de derechos y que introduzca un procedimiento de regularización permanente.',
            policyInstrument: 'Procedimiento de regularización permanente y cierre de los CIEs',
            section: 'Puntos 4 y 10 · Páginas 104 y 105',
            qualifications: [
              'Cierre inmediato de todos los Centros de Internamiento de Extranjeros (CIE).',
              'Acceso universal efectivo a la cobertura del Sistema Nacional de Salud.'
            ],
            source: 'Un Programa para ti · Puntos 4 y 10, págs. 104 y 105',
            sourceUrl: 'https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf#page=104',
            date: '06/07/2023'
          },
          'erc': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Establecer vías legales y seguras de entrada, fin inmediato de las devoluciones en caliente y cierre de centros de detención.',
            quote: 'Establir vies legals i segures d\'entrada a l’Estat espanyol, per a garantir l’accés a la lliure circulació i al dret d’asil a les persones desplaçades forçosament, davant les vulneracions en l’accés a l’asil',
            policyInstrument: 'Vías legales y seguras de entrada y fin de devoluciones en caliente',
            section: 'Drets de Ciutadania · Página 38 (impresa 37)',
            qualifications: [
              'Derogación de la disposición sobre rechazos en frontera en Ceuta y Melilla.',
              'Incremento de visados humanitarios y de reagrupación familiar.'
            ],
            source: 'Programa Electoral 2023 · Drets, pág. 38 (impresa 37)',
            sourceUrl: 'https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf#page=38',
            date: '07/07/2023'
          },
          'pnv': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Transferencia a Euskadi de las competencias en políticas migratorias y aplicación de alternativas a la privación de libertad en los CIE.',
            quote: 'Transferencia a la CAV de las políticas migratorias y defensa del modelo vasco de acogida (...) velaremos por la aplicación de alternativas a la privación de libertad en los Centros de Internamiento de Extranjeros (CIE)',
            policyInstrument: 'Transferencia estatutaria de políticas migratorias y acogida vasca',
            section: 'Derechos Humanos y Convivencia · Página 11 (impresa 11)',
            qualifications: [
              'Defensa del modelo vasco de acogida e integración comunitaria.',
              'Reforma urgente del reglamento de los CIE para garantizar derechos humanos.'
            ],
            source: 'Con voz propia · Punto 5, pág. 11 (impresa 11)',
            sourceUrl: 'https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j#page=11',
            date: '07/07/2023'
          }
        },
        relationships: {
          'pp:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre control e inspección fronteriza con FRONTEX (PP) frente a regularización permanente de derechos y cierre de CIEs (Sumar).',
            differences: [
              'El PP prioriza la seguridad fronteriza, acuerdos de retorno en origen y aumento policial.',
              'Sumar propone regularización permanente en la LOEX, cierre de todos los CIEs y sanidad universal sin barreras.'
            ]
          },
          'pp:erc': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre refuerzo policial de fronteras (PP) y fin de devoluciones en caliente con vías legales seguras (ERC).',
            differences: [
              'El PP defiende la participación en FRONTEX y el nuevo sistema europeo de control de entradas.',
              'ERC exige derogar los rechazos en frontera en Ceuta y Melilla y garantizar el asilo efectivo.'
            ]
          },
          'pp:pnv': {
            type: 'divergence',
            typeLabel: 'Discrepancia competencial',
            icon: '≠',
            summary: 'Discrepancia entre la gestión estatal centralizada de fronteras (PP) y la transferencia estatutaria de políticas migratorias a Euskadi (PNV).',
            differences: [
              'El PP aboga por una Autoridad Nacional única para coordinar la política migratoria.',
              'El PNV reclama la transferencia del modelo de acogida y alternativas a la privación en los CIE.'
            ]
          },
          'erc:sumar': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Coincidencia en garantizar los derechos humanos de las personas migrantes, vías legales y alternativas al internamiento.',
            differences: [
              'Sumar enfatiza la reforma legislativa de la LOEX para regularización permanente.',
              'ERC prioriza el fin de las devoluciones en caliente y los visados humanitarios de asilo.'
            ]
          },
          'erc:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en la descentralización de la acogida y la defensa de los derechos de las personas migrantes frente a los CIE.',
            differences: [
              'ERC se enfoca en el cese de expulsiones colectivas y garantías en frontera sur.',
              'El PNV demanda la transferencia estatutaria completa del sistema de acogida e integración a Euskadi.'
            ]
          },
          'pnv:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en el enfoque garantista y alternativo a los CIE, con diferente acento competencial autonómico.',
            differences: [
              'Sumar promueve una reforma general de la LOEX y cierre estatal de todos los centros de internamiento.',
              'El PNV prioriza la gestión y gobernanza de la acogida desde las instituciones vascas.'
            ]
          }
        }
      },
      {
        id: 'immigration-regularization',
        title: 'Medida: Canales de regularización y autorizaciones de residencia',
        summary: 'Gestión de flujos migratorios, procedimientos de asilo y cooperación en origen.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Agilización de trámites de arraigo social y laboral y apoyo a la iniciativa de regularización extraordinaria.',
            qualifications: ['Cumplimiento de requisitos de empadronamiento continuo y carencia de antecedentes penales.'],
            source: 'Programa de ejemplo v1.0 · pág. 62',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=62',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Vinculación estricta de las autorizaciones de entrada y residencia a contratos de trabajo en origen según catálogo de ocupaciones.',
            qualifications: ['Coordinación con organizaciones empresariales sectoriales.'],
            source: 'Manifiesto parcial v0.9 · pág. 26',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=26',
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'divergence',
            typeLabel: 'Diferencia en instrumento o alcance',
            icon: '↔',
            summary: 'Partido A promueve flexibilización por vías de arraigo; Partido B condiciona la residencia a la contratación previa formal en el país de origen.',
            differences: [
              'Vía de acceso: regularización sobre situación de hecho frente a canal exclusivo de contratación en origen.'
            ]
          }
        }
      },
      {
        id: 'immigration-reception-centers',
        title: 'Medida: Gestión y condiciones de los centros de acogida humanitaria',
        summary: 'Infraestructuras de atención a solicitantes de asilo y tutela coordinada de menores.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Ampliación de plazas de acogida humanitaria y redistribución territorial vinculante de menores migrantes no acompañados.',
            qualifications: ['Modificación de la Ley de Extranjería acordada con comunidades autónomas.'],
            source: 'Programa de ejemplo v1.0 · pág. 64',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=64',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'El programa revisado no incluye una propuesta explícita sobre el modelo de centros de acogida.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Manifiesto parcial v0.9',
            sourceUrl: null,
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido A detalla un mecanismo vinculante de reparto de menores, mientras que en el documento de Partido B no consta propuesta específica.',
            differences: ['«No consta» no implica oposición política.']
          }
        }
      }
    ],

    'foreign-policy-eu': [
      {
        id: 'foreign-pilot-2023-measure',
        electionId: 'es-gen-2023',
        title: 'Medida: Autonomía estratégica europea, compromisos de defensa y política exterior (2023)',
        summary: 'Propuestas de los programas electorales del 23J de 2023 sobre el gasto en defensa, alianzas de seguridad atlántica, diplomacia y autonomía estratégica de la Unión Europea.',
        context: 'Esta iniciativa contrasta las visiones en política exterior y seguridad: alineamiento con la OTAN y refuerzo de capacidades industriales de defensa frente a diplomacia de desescalada, control de venta de armas y subordinación de la geopolítica a los derechos humanos.',
        keyAxes: [
          'Alianzas militares y defensa: desarrollo de base tecnológica de defensa complementaria a la OTAN frente a desnuclearización y auditoría del gasto militar.',
          'Autonomía europea: fortalecimiento del pilar de seguridad comunitario frente a una autonomía civil y no militarizada.',
          'Prioridades exteriores: diplomacia basada en intereses estratégicos y alianzas estatales frente a primacía absoluta de los derechos humanos y derecho internacional.'
        ],
        positions: {
          'pp': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Impulsar una autonomía estratégica europea abierta complementaria con la OTAN y fortalecer la base tecnológica e industrial de la defensa.',
            quote: 'IMPULSAREMOS UNA AUTONOMÍA ESTRATÉGICA ABIERTA que desarrolle una Europa de la seguridad y la defensa, así como una base industrial y tecnológica europea, complementaria de la Alianza Atlántica.',
            policyInstrument: 'Autonomía estratégica europea ligada a la OTAN y base industrial de defensa',
            section: 'Medida 314 · Página 99 (impresa 97)',
            qualifications: [
              'Complementariedad obligada con la Alianza Atlántica.',
              'Estrategia industrial para sectores aeroespacial y de defensa.'
            ],
            source: 'Programa Electoral PP 23J · Medida 314, pág. 99 (impresa 97)',
            sourceUrl: 'https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf#page=99',
            date: '06/07/2023'
          },
          'sumar': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Revisión y auditoría del gasto en armamento, prohibición de venta de armas a violadores de derechos humanos y diplomacia de paz.',
            quote: 'Promoveremos la revisión y auditoría de los Programas Especiales de Armamento y otros gastos asociados a planes de defensa con el fin de dotarlos de mayor transparencia.',
            policyInstrument: 'Auditoría del gasto militar y autonomía estratégica civil no militarizada',
            section: 'Punto 3 · Página 139',
            qualifications: [
              'Prohibición de exportaciones armamentísticas a países con vulneraciones de derechos.',
              'Firma y ratificación del Tratado sobre la Prohibición de las Armas Nucleares.'
            ],
            source: 'Un Programa para ti · Punto 3, pág. 139',
            sourceUrl: 'https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf#page=139',
            date: '06/07/2023'
          },
          'erc': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Rechazo al incremento del gasto militar de la OTAN, apuesta por el desarme global y reorientación de recursos a gasto social.',
            quote: 'que a escala global aposti per la cooperació, el desarmament i la desnuclearització davant dels conflictes internacionals (...) reducció de la despesa militar i reconversió de la indústria armamentista.',
            policyInstrument: 'Reducción del gasto militar y reconversión de la industria armamentística',
            section: 'Pau i Seguretat · Página 29 (impresa 28)',
            qualifications: [
              'Crítica al objetivo de gasto en defensa del 2% del PIB.',
              'Exigencia de no participación en misiones armadas fuera del amparo de la ONU.'
            ],
            source: 'Programa Electoral 2023 · Pau, pág. 29 (impresa 28)',
            sourceUrl: 'https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf#page=29',
            date: '07/07/2023'
          },
          'pnv': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Política exterior guiada por los derechos humanos y la cooperación internacional, sin supeditar los principios a intereses geopolíticos.',
            quote: 'Una política exterior comprometida con los Derechos Humanos que no los deje en la cuneta en aras a otros supuestos intereses. Los intereses de la geopolítica no pueden hacer que el discurso humanista (...) quede en entredicho',
            policyInstrument: 'Diplomacia humanista y blindaje presupuestario de la cooperación internacional',
            section: 'Acción Exterior · Página 11 (impresa 11)',
            qualifications: [
              'Compromiso presupuestario suficiente con las partidas de cooperación al desarrollo.',
              'Alineamiento con los tratados de Derecho Internacional Humanitario.'
            ],
            source: 'Con voz propia · Punto 6, pág. 11 (impresa 11)',
            sourceUrl: 'https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j#page=11',
            date: '07/07/2023'
          }
        },
        relationships: {
          'pp:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre una autonomía estratégica complementaria de la OTAN (PP) frente a una auditoría del gasto militar y diplomacia civil (Sumar).',
            differences: [
              'El PP defiende la alianza atlántica y una base industrial tecnológica de defensa fuerte.',
              'Sumar exige auditoría del gasto en armamento, prohibir venta de armas y un multilateralismo pacífico.'
            ]
          },
          'pp:erc': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre el alineamiento con la OTAN (PP) y la oposición frontal al gasto militar y desarme internacional (ERC).',
            differences: [
              'El PP apoya los compromisos atlánticos y la industria aeroespacial y de defensa.',
              'ERC rechaza el objetivo de gasto del 2% del PIB y pide reconvertir la industria armamentista hacia gasto social.'
            ]
          },
          'pp:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en el europeísmo y la inserción internacional de España, con mayor énfasis del PNV en la primacía de derechos humanos sobre la geopolítica.',
            differences: [
              'El PP sitúa la defensa de los intereses nacionales y la OTAN como eje exterior prioritario.',
              'El PNV exige que los intereses geoestratégicos no releguen los compromisos de cooperación y derechos humanos.'
            ]
          },
          'erc:sumar': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Coincidencia en el desarme, la crítica al aumento del gasto militar y la prohibición de armas nucleares.',
            differences: [
              'Sumar detalla la auditoría de programas especiales de armamento y diplomacia climática.',
              'ERC centra su propuesta en la reducción presupuestaria del gasto militar y la soberanía de los pueblos.'
            ]
          },
          'erc:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en la defensa del derecho internacional humanitario y la ayuda al desarrollo frente a la lógica de bloques.',
            differences: [
              'ERC rechaza de forma explícita las metas de gasto militar impuestas por la OTAN.',
              'El PNV prioriza el fortalecimiento de la cooperación internacional y los consensos democráticos occidentales.'
            ]
          },
          'pnv:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en vincular la acción exterior a los derechos humanos y la cooperación solidaria, con matices sobre las alianzas tradicionales.',
            differences: [
              'Sumar aboga por una reformulación profunda del multilateralismo global y revisión del gasto de defensa.',
              'El PNV defiende los principios humanistas y la cooperación al desarrollo dentro del marco europeo.'
            ]
          }
        }
      },
      {
        id: 'foreign-defense-spending',
        title: 'Medida: Compromisos presupuestarios de gasto en defensa y OTAN',
        summary: 'Cumplimiento de objetivos de gasto militar en el marco de la OTAN y alianzas europeas.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Alcanzar el objetivo del 2% del PIB en defensa en el horizonte de 2029 con prioridad en la industria nacional y ciberseguridad.',
            qualifications: ['Sujeto a la senda acordada en la cumbre de la OTAN.'],
            source: 'Programa de ejemplo v1.0 · pág. 70',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=70',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Acelerar la inversión militar para alcanzar el 2% del PIB antes de 2027 y reforzar el pilar europeo de defensa.',
            qualifications: ['Revisión anual de contratos plurianuales de armamento.'],
            source: 'Manifiesto parcial v0.9 · pág. 30',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=30',
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '~',
            summary: 'Ambas formaciones comparten la meta del 2% del PIB en defensa, pero difieren en los plazos de cumplimiento temporal.',
            differences: [
              'Horizonte temporal: año 2029 (Partido A) frente a año 2027 (Partido B).'
            ]
          }
        }
      },
      {
        id: 'foreign-eu-fiscal-rules',
        title: 'Medida: Gobernanza económica de la UE y reglas fiscales',
        summary: 'Posición ante los marcos de déficit y deuda comunitaria y fondos de cohesión.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Defensa de sendas de ajuste fiscal graduales que excluyan las inversiones verdes y de digitalización del cómputo de déficit.',
            qualifications: ['Negociación en el Ecofin.'],
            source: 'Programa de ejemplo v1.0 · pág. 72',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=72',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'No consta propuesta específica sobre cláusulas de inversión en las reglas fiscales comunitarias.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Manifiesto parcial v0.9',
            sourceUrl: null,
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido A plantea excepciones para inversiones verdes; Partido B no registra propuesta detallada en este documento.',
            differences: ['«No consta» no implica oposición política.']
          }
        }
      }
    ],

    'climate-energy': [
      {
        id: 'climate-pilot-2023-measure',
        electionId: 'es-gen-2023',
        title: 'Medida: Despliegue de energías renovables y modelo de transición energética (2023)',
        summary: 'Propuestas de los programas electorales del 23J de 2023 sobre el ritmo de despliegue de energías renovables, simplificación administrativa y el calendario de fuentes de generación energética.',
        context: 'Esta iniciativa contrasta las estrategias ante la transición ecológica: agilización burocrática y prolongación de la vida útil de las centrales nucleares frente a la moratoria nuclear con cierre ordenado y el fomento de comunidades energéticas locales de proximidad.',
        keyAxes: [
          'Calendario de generación: extensión de la vida útil de las centrales nucleares frente a cumplimiento estricto del calendario de cierre del parque nuclear.',
          'Despliegue renovable: agilización burocrática con tasa por hito a promotores frente a prioridad en autoconsumo social y comunidades locales de proximidad.',
          'Modelo de red: planificación centralizada y capacidad de evacuación frente a generación distribuida de km0 y soberanía energética territorial.'
        ],
        positions: {
          'pp': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Desbloquear la tramitación de energías renovables con una tasa por hito y proponer la extensión de la vida útil de las centrales nucleares.',
            quote: 'DESBLOQUEAREMOS EL PROCESO DE CONCESIÓN DE PERMISOS Y APROBACIÓN EN LA INSTALACIÓN DE RENOVABLES. Para ello, introduciremos una “tasa por hito” que, con cargo al promotor del proyecto, financie el incremento de los medios necesarios',
            policyInstrument: 'Tasa por hito para agilización de renovables y prórroga del parque nuclear',
            section: 'Medidas 112 y 114 · Página 38 (impresa 36)',
            qualifications: [
              'Requiere informe favorable del Consejo de Seguridad Nuclear.',
              'En el marco de la normativa comunitaria europea.'
            ],
            source: 'Programa Electoral PP 23J · Medidas 112 y 114, pág. 38 (impresa 36)',
            sourceUrl: 'https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf#page=38',
            date: '06/07/2023'
          },
          'sumar': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Acelerar la transición ecológica hacia un modelo 100% renovable con autoconsumo y comunidades locales, manteniendo el calendario de cierre nuclear.',
            quote: 'Uno de nuestros objetivos debe ser garantizar una transición energética justa hacia un modelo basado en las energías renovables, a la vez que se asegura la preservación del paisaje y del modelo tradicional de producción en el medio rural.',
            policyInstrument: 'Plan nacional de transición justa, comunidades energéticas y moratoria nuclear',
            section: 'Punto 3 (pág. 11) y Punto 9 (pág. 48)',
            qualifications: [
              'Moratoria a cualquier intento de prolongación de centrales nucleares.',
              'Garantizar la preservación paisajística y del entorno rural.'
            ],
            source: 'Un Programa para ti · Punto 3, pág. 11 y Punto 9, pág. 48',
            sourceUrl: 'https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf#page=11',
            date: '06/07/2023'
          },
          'erc': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Transición ecológica hacia un modelo energético descentralizado, de proximidad y 100% renovable con soberanía energética para Cataluña.',
            quote: 'La transició energètica només pot avançar si transformem un model energètic centralitzat i vertical en un model descentralitzat i distribuït, que prioritzi la generació de km0 i faciliti al consumidor exercir els seus drets',
            policyInstrument: 'Modelo distribuido de generación renovable km0 y soberanía energética',
            section: 'Sostenibilitat · Página 101 (impresa 100)',
            qualifications: [
              'Rechaza monopolios centralizados en el despliegue de renovables.',
              'Prioriza la soberanía energética y de decisión de las instituciones catalanas.'
            ],
            source: 'Programa Electoral 2023 · Sec. b, pág. 101 (impresa 100)',
            sourceUrl: 'https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf#page=101',
            date: '07/07/2023'
          },
          'pnv': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Acelerar el despliegue de energías renovables agilizando tramitaciones dentro de un marco regulatorio estable para la competitividad industrial.',
            quote: 'necesitamos un nuevo modelo energético basado en un mix de energías y nuevas tecnologías que permitan una transición sostenible (...) Una aceleración de la implantación de energías renovables, agilizando los procesos de tramitación.',
            policyInstrument: 'Aceleración de renovables y marco regulatorio de certidumbre inversora',
            section: 'Energía e Industria · Página 20 (impresa 20)',
            qualifications: [
              'Garantizar el equilibrio entre descarbonización y competitividad de los costes industriales.',
              'Respeto al régimen de autogobierno en ordenación industrial y medioambiental.'
            ],
            source: 'Con voz propia · Punto 7, pág. 20 (impresa 20)',
            sourceUrl: 'https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j#page=20',
            date: '07/07/2023'
          }
        },
        relationships: {
          'pp:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre la prórroga de las centrales nucleares y tasa por hito (PP) frente a moratoria nuclear y comunidades energéticas de proximidad (Sumar).',
            differences: [
              'El PP propone extender la vida útil de las centrales nucleares y acelerar permisos con tasa a promotores.',
              'Sumar defiende el cumplimiento del calendario de cierre nuclear sin prórrogas y la transición justa.'
            ]
          },
          'pp:erc': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre la prolongación nuclear y red centralizada (PP) frente a modelo 100% renovable descentralizado y de proximidad (ERC).',
            differences: [
              'El PP apuesta por un mix que preserve la energía nuclear como respaldo y agilización administrativa estatal.',
              'ERC aboga por un modelo descentralizado de km0 y soberanía energética catalana libre de monopolios.'
            ]
          },
          'pp:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en la necesidad de agilizar trámites de renovables y asegurar certidumbre inversora para la industria.',
            differences: [
              'El PP incluye la propuesta explícita de extender la vida útil de las centrales nucleares.',
              'El PNV enfoca sus medidas en el mix sostenible adaptado a la competitividad de costes de la industria vasca.'
            ]
          },
          'erc:sumar': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Coincidencia en avanzar hacia un modelo 100% renovable, autoconsumo ciudadano y rechazo a prolongar la energía nuclear.',
            differences: [
              'Sumar plantea un plan nacional de transición justa con mecanismos de subastas y almacenamiento.',
              'ERC recalca la soberanía energética de Cataluña y el modelo distribuido frente a oligopolios estatales.'
            ]
          },
          'erc:pnv': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en la defensa del autogobierno territorial en energía y aceleración de renovables.',
            differences: [
              'ERC prioriza el modelo de generación distribuida de km0 y transición 100% renovable.',
              'El PNV enfatiza la estabilidad de precios para empresas electrointensivas e industria manufacturera.'
            ]
          },
          'pnv:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en acelerar la implantación renovable, con distinta ponderación entre costes industriales y preservación rural.',
            differences: [
              'Sumar recalca la protección del paisaje rural y la moratoria sin excepciones al calendario nuclear.',
              'El PNV pone el acento en la competitividad de precios y contratos PPA para el tejido industrial.'
            ]
          }
        }
      },
      {
        id: 'climate-decarbonization',
        title: 'Medida: Calendario de descarbonización y cierre de generación fósil/nuclear',
        summary: 'Transición energética, despliegue de mix renovable y calendario de clausura de centrales.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Mantenimiento del calendario de cierre ordenado de las centrales nucleares entre 2027 y 2035 y aceleración de renovables.',
            qualifications: ['Supeditado a garantizar la seguridad de suministro de la red por Red Eléctrica.'],
            source: 'Programa de ejemplo v1.0 · pág. 78',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=78',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Prolongación de la vida útil del parque nuclear español como tecnología de respaldo sin emisiones de CO2.',
            qualifications: ['Sujeto a dictamen preceptivo de seguridad del Consejo de Seguridad Nuclear.'],
            source: 'Manifiesto parcial v0.9 · pág. 34',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=34',
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'divergence',
            typeLabel: 'Diferencia en instrumento o alcance',
            icon: '↔',
            summary: 'Partido A aboga por el cierre progresivo programado del parque nuclear; Partido B propone extender su vida operativa como energía de respaldo.',
            differences: [
              'Modelo de generación: desmantelamiento programado frente a extensión de la explotación comercial.'
            ]
          }
        }
      },
      {
        id: 'climate-renewables-deployment',
        title: 'Medida: Despliegue de energías renovables y participación ciudadana',
        summary: 'Ordenación territorial de proyectos renovables y fomento de comunidades energéticas locales.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Exigir participación mínima del 20% del capital social para municipios y cooperativas locales en grandes proyectos renovables.',
            qualifications: ['Aplica a instalaciones superiores a 5 MW de potencia instalada.'],
            source: 'Programa de ejemplo v1.0 · pág. 81',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=81',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'El programa revisado no incluye porcentajes específicos de participación ciudadana en proyectos renovables.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Manifiesto parcial v0.9',
            sourceUrl: null,
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido A propone cuotas de participación ciudadana en parques renovables; Partido B no registra posición en esta medida.',
            differences: ['«No consta» no implica oposición política.']
          }
        }
      }
    ],

    'institutions-rights': [
      {
        id: 'institutions-pilot-2023-measure',
        electionId: 'es-gen-2023',
        title: 'Medida: Reforma del sistema de elección del CGPJ y gobernanza judicial (2023)',
        summary: 'Propuestas de los programas electorales del 23J de 2023 sobre la renovación del Consejo General del Poder Judicial (CGPJ), el sistema de elección de los vocales judiciales y la estructura institucional de la justicia.',
        context: 'Esta iniciativa contrasta las alternativas para desbloquear y reformar el órgano de gobierno de los jueces: elección corporativa directa de los doce vocales judiciales por la carrera frente a la primacía del mandato parlamentario y la creación de consejos autonómicos de justicia.',
        keyAxes: [
          'Sistema de elección: elección directa de vocales judiciales por jueces y magistrados frente a elección por el Parlamento para asegurar el pluralismo democrático.',
          'Mecanismos antibloqueo: cese automático al expirar el mandato frente a derogación de reformas que limitan funciones con mandato caducado.',
          'Descentralización judicial: mantenimiento de cúpula estatal única frente a transferencias y creación de consejos autonómicos de justicia.'
        ],
        positions: {
          'pp': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Reforma de la LOPJ para que los 12 vocales judiciales del CGPJ sean elegidos directamente por jueces y magistrados, derogando límites a sus funciones.',
            quote: 'mediante la reforma de su ley Orgánica, incluyendo la modificación del sistema de elección de los miembros del Consejo de manera que sean los jueces y magistrados los que elijan a los 12 vocales de procedencia judicial.',
            policyInstrument: 'Reforma de la LOPJ para elección corporativa de los vocales judiciales',
            section: 'Medida 237 · Página 75 (impresa 73)',
            qualifications: [
              'Exclusivo para los 12 vocales de extracción judicial.',
              'Derogación de la limitación legal de nombramientos del CGPJ en funciones.'
            ],
            source: 'Programa Electoral PP 23J · Medida 237, pág. 75 (impresa 73)',
            sourceUrl: 'https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf#page=75',
            date: '06/07/2023'
          },
          'sumar': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Reformular la elección del CGPJ reforzando la representación parlamentaria democrática, mayorías antibloqueo y cese automático tras expirar el mandato.',
            quote: 'Para eso es preciso reformular su sistema de elección y reforzar su naturaleza democrática y, por tanto, el protagonismo del Parlamento, así como la obtención de mayorías, de modo que se evite el bloqueo que en la actualidad sufre',
            policyInstrument: 'Reforma del sistema parlamentario de elección y cese automático por caducidad',
            section: 'Punto 20 · Página 129',
            qualifications: [
              'Mantenimiento de la legitimidad de origen parlamentario para todos los vocales.',
              'Cese automático inmediato de vocales y presidencia una vez expirado el mandato legal.'
            ],
            source: 'Un Programa para ti · Punto 20, pág. 129',
            sourceUrl: 'https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf#page=129',
            date: '06/07/2023'
          },
          'erc': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Denuncia del control partidista de la cúpula judicial española y exigencia de democratización y control ciudadano sobre el poder judicial.',
            quote: 'els principals partits polítics espanyols es neguen a modificar un sistema d’elecció dels membres del govern del poder judicial, que són escollits de manera partidista. Tot plegat afavoreix la ingerència dels partits en les decisions judicials',
            policyInstrument: 'Democratización radical y mecanismos de control ciudadano de la justicia',
            section: 'Justícia · Página 18 (impresa 17)',
            qualifications: [
              'Crítica al modelo bipartidista de reparto de cuotas en el CGPJ.',
              'Defensa de la soberanía judicial de la futura República Catalana.'
            ],
            source: 'Programa Electoral 2023 · Justícia, pág. 18 (impresa 17)',
            sourceUrl: 'https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf#page=18',
            date: '07/07/2023'
          },
          'pnv': {
            status: 'official',
            statusLabel: 'Programa oficial (2023)',
            statement: 'Atribuir el gobierno del Poder Judicial en Euskadi a un Consejo Vasco de Justicia y dotar de plenas funciones a la Ertzaintza como policía judicial.',
            quote: 'Asimismo, el gobierno del Poder Judicial en el ámbito de Euskadi correspondería al Consejo Vasco de Justicia, al tiempo que la Ertzaintza sería, en todos los casos, la Policía judicial en el ámbito vasco.',
            policyInstrument: 'Creación del Consejo Vasco de Justicia y traspaso de gobernanza judicial',
            section: 'Autogobierno y Justicia · Página 9 (impresa 9)',
            qualifications: [
              'Supeditado al reconocimiento foral y estatutario de autogobierno en justicia.'
            ],
            source: 'Con voz propia · Punto 2, pág. 9 (impresa 9)',
            sourceUrl: 'https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j#page=9',
            date: '07/07/2023'
          }
        },
        relationships: {
          'pp:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre la elección directa de los 12 vocales judiciales por la carrera judicial (PP) frente al protagonismo democrático del Parlamento (Sumar).',
            differences: [
              'El PP propone reformar la LOPJ para que jueces y magistrados elijan a sus 12 vocales directamente.',
              'Sumar defiende mantener la legitimidad parlamentaria de todos los vocales e introducir el cese automático por caducidad.'
            ]
          },
          'pp:erc': {
            type: 'divergence',
            typeLabel: 'Discrepancia en la medida',
            icon: '≠',
            summary: 'Discrepancia entre la reforma corporativa del CGPJ estatal (PP) frente a la denuncia del sesgo judicial y defensa de la soberanía catalana (ERC).',
            differences: [
              'El PP busca aislar al órgano de gobierno judicial mediante la elección interna de jueces.',
              'ERC califica la cúpula judicial de ilegítima y partidista y reclama control ciudadano y justicia propia.'
            ]
          },
          'pp:pnv': {
            type: 'divergence',
            typeLabel: 'Discrepancia competencial',
            icon: '≠',
            summary: 'Discrepancia entre un modelo judicial estatal único (PP) frente a la creación de un Consejo Vasco de Justicia (PNV).',
            differences: [
              'El PP defiende la unidad del poder judicial y de su órgano de gobierno central.',
              'El PNV reclama descentralizar la gobernanza de la justicia a las instituciones vascas.'
            ]
          },
          'erc:sumar': {
            type: 'qualification',
            typeLabel: 'Coincidencia parcial con matices',
            icon: '≈',
            summary: 'Coincidencia en criticar el bloqueo conservador y el uso partidista del CGPJ, con diferente propuesta de salida.',
            differences: [
              'Sumar propone reformular las mayorías parlamentarias antibloqueo y reforzar la paridad.',
              'ERC sostiene que el modelo del 78 no es reformable y propugna la ruptura y control ciudadano de la justicia.'
            ]
          },
          'erc:pnv': {
            type: 'agreement',
            typeLabel: 'Coincidencia en la medida',
            icon: '✓',
            summary: 'Coincidencia en rechazar el modelo judicial centralizado y reivindicar el autogobierno en materia de justicia.',
            differences: [
              'ERC enfatiza los derechos lingüísticos y el fin de la cúpula judicial politizada.',
              'El PNV plantea formalmente la instauración estatutaria del Consejo Vasco de Justicia y policía judicial foral.'
            ]
          },
          'pnv:sumar': {
            type: 'divergence',
            typeLabel: 'Discrepancia competencial',
            icon: '≠',
            summary: 'Discrepancia entre la reforma parlamentaria del órgano central (Sumar) frente a la descentralización al Consejo Vasco de Justicia (PNV).',
            differences: [
              'Sumar busca desbloquear y legitimar el CGPJ como órgano de alcance estatal común.',
              'El PNV sitúa la solución en transferir las competencias de gobierno judicial a Euskadi.'
            ]
          }
        }
      },
      {
        id: 'institutions-cgpj',
        title: 'Medida: Sistema de elección y renovación del Consejo General del Poder Judicial',
        summary: 'Reformas institucionales, sistema de elección del CGPJ y mayorías parlamentarias.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Mantener la potestad de las Cortes Generales para elegir a los 20 vocales por mayoría cualificada de tres quintos.',
            qualifications: ['Mecanismo de desbloqueo mediante mayoría absoluta en segunda votación tras plazo legal.'],
            source: 'Programa de ejemplo v1.0 · pág. 88',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=88',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'partial',
            statusLabel: 'Documento parcial',
            statement: 'Reforma de la Ley Orgánica del Poder Judicial para que los doce vocales judiciales sean elegidos directamente por los jueces.',
            qualifications: ['Conforme a las recomendaciones de la Comisión Europea sobre el Estado de Derecho.'],
            source: 'Manifiesto parcial v0.9 · pág. 38',
            sourceUrl: 'https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf#page=38',
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'divergence',
            typeLabel: 'Diferencia en instrumento o alcance',
            icon: '↔',
            summary: 'Partido A defiende la elección parlamentaria íntegra de los vocales; Partido B propone que los 12 vocales de procedencia judicial sean elegidos directamente por la carrera judicial.',
            differences: [
              'Órgano elector de los vocales judiciales: Cortes Generales frente a sufragio corporativo de jueces y magistrados.'
            ]
          }
        }
      },
      {
        id: 'institutions-territorial-funding',
        title: 'Medida: Modelo de financiación autonómica y nivelación territorial',
        summary: 'Reforma de la Ley de Financiación de las Comunidades Autónomas (LOFCA) y cohesión de servicios públicos.',
        positions: {
          'party-a': {
            status: 'official',
            statusLabel: 'Programa oficial',
            statement: 'Reforma de la financiación autonómica garantizando la suficiencia financiera y un fondo de nivelación interterritorial.',
            qualifications: ['Aprobación en el Consejo de Política Fiscal y Financiera.'],
            source: 'Programa de ejemplo v1.0 · pág. 92',
            sourceUrl: 'https://partido-ejemplo-a.es/programa-2026.pdf#page=92',
            date: '16/10/2026'
          },
          'party-b': {
            status: 'missing',
            statusLabel: 'No consta en el programa',
            statement: 'El programa revisado no incluye una propuesta cerrada sobre los fondos del sistema de financiación autonómica.',
            explanation: 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
            qualifications: [],
            source: 'Manifiesto parcial v0.9',
            sourceUrl: null,
            date: '16/10/2026'
          }
        },
        relationships: {
          'party-a:party-b': {
            type: 'notFound',
            typeLabel: 'Sin posición comparable en esta medida',
            icon: '—',
            summary: 'Partido A plantea un fondo de nivelación estatal de servicios; en el documento de Partido B no consta propuesta específica.',
            differences: ['«No consta» no implica oposición política.']
          }
        }
      }
    ]
  };

  function getPartyData(partyKey) {
    if (PARTIES[partyKey]) {
      return PARTIES[partyKey];
    }
    // Fallback party object
    return {
      id: partyKey,
      name: partyKey,
      shortName: partyKey.toUpperCase(),
      pill: partyKey.slice(0, 3).toUpperCase(),
      pillClass: 'party-pill-a',
      status: 'missing',
      statusLabel: 'Programa no disponible',
      isFixture: false
    };
  }

  function fixturePositionKey(partyKey) {
    // Generated selectors use schema IDs; the local fixtures use shorter keys.
    const aliases = {
      'partido-ejemplo-a': 'party-a',
      'partido-ejemplo-b': 'party-b',
      'coalicion-ejemplo-c': 'coalicion-c',
      'partido-ejemplo-d': 'party-d'
    };
    return aliases[partyKey] || partyKey;
  }

  function getPositionForParty(measure, partyKey) {
    const partyData = getPartyData(partyKey);
    const positionKey = fixturePositionKey(partyKey);

    // Check direct match in measure.positions
    if (measure.positions && measure.positions[positionKey]) {
      const pos = measure.positions[positionKey];
      return {
        name: partyData.name,
        pill: partyData.pill,
        pillClass: partyData.pillClass,
        status: pos.status || partyData.status,
        statusLabel: pos.statusLabel || partyData.statusLabel,
        statement: pos.statement,
        quote: pos.quote || null,
        policyInstrument: pos.policyInstrument || null,
        section: pos.section || null,
        qualifications: pos.qualifications || [],
        explanation: pos.explanation || null,
        source: pos.source || 'Registro oficial de fuentes',
        sourceUrl: pos.sourceUrl || null,
        date: pos.date || '09/10/2026'
      };
    }

    // Default missing/pending state for parties without explicit position
    const isMissingProg = partyData.status === 'missing';
    return {
      name: partyData.name,
      pill: partyData.pill,
      pillClass: partyData.pillClass,
      status: 'missing',
      statusLabel: isMissingProg ? 'Programa no disponible' : 'No consta en el programa',
      statement: isMissingProg
        ? 'El programa oficial para las elecciones generales de 2026 aún no ha sido publicado por la candidatura.'
        : 'El programa revisado no incluye una propuesta explícita sobre esta medida concreta.',
      quote: null,
      policyInstrument: null,
      section: null,
      qualifications: [],
      explanation: isMissingProg
        ? 'La ausencia de un programa publicado no debe interpretarse como oposición ni como apoyo a esta medida concreta.'
        : 'La ausencia de una medida en el programa no debe interpretarse como oposición ni como apoyo.',
      source: isMissingProg
        ? 'Registro oficial de fuentes (seguimiento 2026)'
        : 'Programa analizado',
      sourceUrl: null,
      date: '09/10/2026'
    };
  }

  function getRelationshipForPair(measure, partyAKey, partyBKey, posA, posB) {
    // 1. Direct relationship key check
    const key1 = fixturePositionKey(partyAKey) + ':' + fixturePositionKey(partyBKey);
    const key2 = fixturePositionKey(partyBKey) + ':' + fixturePositionKey(partyAKey);

    if (measure.relationships && (measure.relationships[key1] || measure.relationships[key2])) {
      return measure.relationships[key1] || measure.relationships[key2];
    }

    // 2. Synthesize relationship based on position statuses
    const partyAData = getPartyData(partyAKey);
    const partyBData = getPartyData(partyBKey);

    if (posA.status === 'missing' && posB.status === 'missing') {
      return {
        type: 'notFound',
        typeLabel: 'Sin propuestas publicadas',
        icon: '—',
        summary: 'Ninguna de las dos formaciones dispone de una propuesta revisada sobre esta medida concreta en los documentos analizados.',
        differences: ['«No consta» nunca se interpretará como oposición política ni como acuerdo tácito.']
      };
    }

    if (posA.status === 'missing' || posB.status === 'missing') {
      const activeParty = posA.status !== 'missing' ? partyAData.shortName : partyBData.shortName;
      const missingParty = posA.status === 'missing' ? partyAData.shortName : partyBData.shortName;
      return {
        type: 'notFound',
        typeLabel: 'Sin posición comparable en esta medida',
        icon: '—',
        summary: activeParty + ' dispone de propuesta en esta medida, mientras que en las fuentes oficiales de ' + missingParty + ' no consta posición registrada.',
        differences: [
          missingParty + ' no registra mención en su documento analizado; la ausencia no constituye oposición.'
        ]
      };
    }

    // Default neutral comparison when both parties have official/partial positions but no specific relationship fixture
    return {
      type: 'qualification',
      typeLabel: 'Propuestas en análisis comparativo',
      icon: '~',
      summary: 'Ambas candidaturas formulan propuestas sobre este ámbito temático con matices operativos propios de cada programa.',
      differences: [
        'Consulte las citas textuales y las condiciones registradas en las tarjetas superiores.'
      ]
    };
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function renderPartyCardHtml(pos, partyLetter, measureIdx) {
    const isMissing = pos.status === 'missing';
    const cardClass = 'party-card party-card-' + partyLetter.toLowerCase() + (isMissing ? ' party-card-missing' : '');
    const pillClass = 'party-pill party-pill-' + partyLetter.toLowerCase();
    const headingId = 'party-' + partyLetter.toLowerCase() + '-' + measureIdx + '-name';
    const statusBadgeClass = 'status-badge status-badge-' + escapeHtml(pos.status);

    let bodyHtml = '<p class="party-statement' + (isMissing ? ' party-statement-missing' : '') + '">' + escapeHtml(pos.statement) + '</p>';

    if (pos.quote) {
      const caveatsJson = escapeHtml(JSON.stringify(pos.qualifications || []));
      bodyHtml += '<div class="party-quote-wrapper">' +
        '<span class="party-quote-label">Extracto literal del programa:</span>' +
        '<blockquote class="party-quote"><p>«' + escapeHtml(pos.quote) + '»</p></blockquote>' +
        '<button type="button" class="btn-open-manifesto" ' +
        'data-party-name="' + escapeHtml(pos.name) + '" ' +
        'data-party-pill="' + escapeHtml(pos.pill) + '" ' +
        'data-party-pill-class="' + escapeHtml(pos.pillClass) + '" ' +
        'data-status-label="' + escapeHtml(pos.statusLabel) + '" ' +
        'data-source="' + escapeHtml(pos.source) + '" ' +
        'data-section="' + escapeHtml(pos.section || '') + '" ' +
        'data-instrument="' + escapeHtml(pos.policyInstrument || '') + '" ' +
        'data-quote="' + escapeHtml(pos.quote) + '" ' +
        'data-caveats="' + caveatsJson + '" ' +
        'data-source-url="' + escapeHtml(pos.sourceUrl || '') + '" ' +
        'aria-haspopup="dialog">' +
        '<span aria-hidden="true">📖</span> ' +
        '<span>Leer extracto</span>' +
        '</button>' +
        '</div>';
    }

    if (pos.qualifications && pos.qualifications.length > 0) {
      for (let i = 0; i < pos.qualifications.length; i++) {
        bodyHtml += '<div class="party-caveat" role="note" aria-label="Matiz registrado">' +
          '<strong>Matiz o condición:</strong> ' + escapeHtml(pos.qualifications[i]) +
          '</div>';
      }
    }

    if (pos.explanation) {
      bodyHtml += '<p class="missing-explanation">' + escapeHtml(pos.explanation) + '</p>';
    }

    let footerHtml = '';
    if (pos.sourceUrl) {
      footerHtml = '<a class="source-citation" href="' + escapeHtml(pos.sourceUrl) + '" target="_blank" rel="noopener noreferrer">' +
        '<span aria-hidden="true">↗</span> Fuente: <span>' + escapeHtml(pos.source) + '</span>' +
        '<span class="sr-only">(se abre en una ventana nueva)</span>' +
        '</a>';
    } else {
      footerHtml = '<span class="source-citation">' +
        '<span aria-hidden="true">↗</span> Fuente: <em>' + escapeHtml(pos.source) + '</em>' +
        '</span>';
    }

    footerHtml += '<time class="source-date" datetime="2026-10-16">Rev. ' + escapeHtml(pos.date) + '</time>';

    return '<article class="' + cardClass + '" aria-labelledby="' + headingId + '">' +
      '<div class="party-card-header">' +
      '<span class="' + pillClass + '" aria-hidden="true">' + partyLetter + '</span>' +
      '<div class="party-card-meta">' +
      '<h4 id="' + headingId + '" class="party-name">' + escapeHtml(pos.name) + '</h4>' +
      '<span class="' + statusBadgeClass + '">' + escapeHtml(pos.statusLabel) + '</span>' +
      '</div>' +
      '</div>' +
      '<div class="party-card-body">' +
      bodyHtml +
      '</div>' +
      '<div class="party-card-footer">' +
      footerHtml +
      '</div>' +
      '</article>';
  }

  function renderMeasureGroupHtml(measure, topicName, partyAKey, partyBKey, measureIdx) {
    const posA = getPositionForParty(measure, partyAKey);
    const posB = getPositionForParty(measure, partyBKey);
    const rel = getRelationshipForPair(measure, partyAKey, partyBKey, posA, posB);

    const titleId = 'measure-' + measureIdx + '-title';

    // Map relationship type to CSS class
    let relClass = 'rel-callout-not-found';
    if (rel.type === 'agreement') {
      relClass = 'rel-callout-agreement';
    } else if (rel.type === 'divergence') {
      relClass = 'rel-callout-divergence';
    } else if (rel.type === 'qualification' || rel.type === 'partial_overlap') {
      relClass = 'rel-callout-qualification';
    }

    let differencesHtml = '';
    if (rel.differences && rel.differences.length > 0) {
      differencesHtml = '<ul class="analysis-differences">';
      for (let i = 0; i < rel.differences.length; i++) {
        differencesHtml += '<li>' + escapeHtml(rel.differences[i]) + '</li>';
      }
      differencesHtml += '</ul>';
    }

    let contextHtml = '';
    if (measure.context || (measure.keyAxes && measure.keyAxes.length > 0)) {
      contextHtml = '<div class="measure-context" role="region" aria-label="Alcance y claves de la iniciativa">';
      if (measure.context) {
        contextHtml += '<p class="measure-context-desc">' + escapeHtml(measure.context) + '</p>';
      }
      if (measure.keyAxes && measure.keyAxes.length > 0) {
        contextHtml += '<div class="measure-axes">' +
          '<span class="measure-axes-label">Claves de contraste en esta medida:</span>' +
          '<ul class="measure-axes-list">';
        for (let a = 0; a < measure.keyAxes.length; a++) {
          contextHtml += '<li>' + escapeHtml(measure.keyAxes[a]) + '</li>';
        }
        contextHtml += '</ul></div>';
      }
      contextHtml += '</div>';
    }

    return '<article class="measure-group" aria-labelledby="' + titleId + '">' +
      '<div class="measure-head">' +
      '<p class="measure-topic-label">TEMA: ' + escapeHtml(topicName.toUpperCase()) + '</p>' +
      '<h3 id="' + titleId + '" class="measure-title">' + escapeHtml(measure.title) + '</h3>' +
      '<p class="measure-summary">' + escapeHtml(measure.summary) + '</p>' +
      contextHtml +
      '</div>' +
      '<div class="measure-cards">' +
      renderPartyCardHtml(posA, 'A', measureIdx) +
      renderPartyCardHtml(posB, 'B', measureIdx) +
      '</div>' +
      '<aside class="analysis-callout ' + relClass + '" aria-label="Lectura comparada">' +
      '<span class="analysis-icon" aria-hidden="true">' + escapeHtml(rel.icon || '—') + '</span>' +
      '<div>' +
      '<h4>' + escapeHtml(rel.typeLabel) + '</h4>' +
      '<p>' + escapeHtml(rel.summary) + '</p>' +
      differencesHtml +
      '</div>' +
      '</aside>' +
      '</article>';
  }

  function init() {
    const form = document.getElementById('selection-form');
    const topicSelect = document.getElementById('topic-select');
    const partyASelect = document.getElementById('party-a-select');
    const partyBSelect = document.getElementById('party-b-select');
    const errorEl = document.getElementById('selection-error');
    const measuresContainer = document.getElementById('measures-container');

    if (!form || !topicSelect || !partyASelect || !partyBSelect || !errorEl) {
      return;
    }

    const route = window.NeutralSharing.readSelection(window.location.href, TOPICS, PARTIES);
    const initialTopic = route.topic;
    const initialPartyA = route.partyA;
    const initialPartyB = route.partyB;
    const isPilot2023 = route.pilot || document.body.dataset.election === 'es-gen-2023';
    let comparisonActive = Boolean(initialPartyA && initialPartyB);

    if (isPilot2023) {
      const pilotParties = ['pp', 'erc', 'sumar', 'pnv'];
      pilotParties.forEach(function (partyId) {
        if (PARTIES[partyId]) {
          PARTIES[partyId].status = 'official';
          PARTIES[partyId].statusLabel = 'Programa oficial (2023)';
          PARTIES[partyId].electionId = 'es-gen-2023';
        }
      });

      const previewBanner = document.querySelector('.preview-banner');
      if (previewBanner) {
        previewBanner.textContent = 'Generales 2023 (piloto) · Ensayo editorial y de derechos con datos oficiales verificados';
      }
    }

    if (initialTopic) {
      topicSelect.value = initialTopic;
    }
    if (initialPartyA) {
      partyASelect.value = initialPartyA;
    } else if (isPilot2023 && PARTIES['pp']) {
      partyASelect.value = 'pp';
    }
    if (initialPartyB) {
      partyBSelect.value = initialPartyB;
    } else if (isPilot2023 && PARTIES['erc']) {
      partyBSelect.value = 'erc';
    }

    function validateSelection() {
      const partyA = partyASelect.value;
      const partyB = partyBSelect.value;

      if (!Object.prototype.hasOwnProperty.call(TOPICS, topicSelect.value) ||
          !Object.prototype.hasOwnProperty.call(PARTIES, partyA) ||
          !Object.prototype.hasOwnProperty.call(PARTIES, partyB) || partyA === partyB ||
          (isPilot2023 && ![partyA, partyB].every(id => ['pp', 'erc', 'sumar', 'pnv'].includes(id)))) {
        errorEl.textContent = 'Por favor, selecciona dos candidaturas distintas para realizar la comparación.';
        errorEl.classList.remove('sr-only');
        partyASelect.setAttribute('aria-invalid', 'true');
        partyBSelect.setAttribute('aria-invalid', 'true');
        return false;
      }

      // Cross-election isolation check (Task 1.4 / Issue #21)
      const candA = PARTIES[partyA];
      const candB = PARTIES[partyB];
      const electionA = candA && candA.electionId ? candA.electionId : 'es-gen-2026';
      const electionB = candB && candB.electionId ? candB.electionId : 'es-gen-2026';
      if (electionA !== electionB) {
        errorEl.textContent = 'Rechazo de combinación entre elecciones (Tarea 1.4): No se permite comparar candidaturas de elecciones distintas (' + electionA + ' vs ' + electionB + ').';
        errorEl.classList.remove('sr-only');
        partyASelect.setAttribute('aria-invalid', 'true');
        partyBSelect.setAttribute('aria-invalid', 'true');
        return false;
      }

      errorEl.textContent = '';
      errorEl.classList.add('sr-only');
      partyASelect.removeAttribute('aria-invalid');
      partyBSelect.removeAttribute('aria-invalid');
      return true;
    }

    function renderComparison() {
      const isValid = validateSelection();
      if (!isValid) {
        return;
      }

      const topicKey = topicSelect.value;
      const partyAKey = partyASelect.value;
      const partyBKey = partyBSelect.value;

      const topicData = TOPICS[topicKey] || TOPICS['housing'];
      let measures = MEASURES_BY_TOPIC[topicKey] || [
        {
          id: topicKey + '-default',
          title: 'Medida: ' + topicData.name,
          summary: topicData.description,
          positions: {},
          relationships: {}
        }
      ];

      // Filter measures by election
      if (isPilot2023) {
        const pilotMeasures = measures.filter(function (m) {
          return m.electionId === 'es-gen-2023';
        });
        measures = pilotMeasures;
      } else {
        measures = measures.filter(function (m) {
          return !m.electionId || m.electionId === 'es-gen-2026';
        });
      }

      // Dynamically render all grouped measures into measuresContainer
      if (measuresContainer) {
        let allMeasuresHtml = '';
        if (measures.length === 0) {
          allMeasuresHtml = '<div class="empty-measures" role="status" aria-live="polite">' +
            '<p class="empty-measures-icon" aria-hidden="true">—</p>' +
            '<h4 class="empty-measures-title">No hay medidas registradas todavía</h4>' +
            '<p class="empty-measures-desc">No constan propuestas revisadas en el tema <strong>' + escapeHtml(topicData.name) + '</strong> para las candidaturas seleccionadas.</p>' +
            '<p class="empty-measures-note">«No consta» indica ausencia documental en el material analizado; nunca se interpretará como oposición política ni como acuerdo tácito.</p>' +
            '</div>';
        } else {
          for (let i = 0; i < measures.length; i++) {
            allMeasuresHtml += renderMeasureGroupHtml(measures[i], topicData.name, partyAKey, partyBKey, i + 1);
          }
        }
        measuresContainer.innerHTML = allMeasuresHtml;
      }

      if (comparisonActive && window.history && window.history.replaceState) {
        window.history.replaceState({}, '', window.NeutralSharing.stableUrl(window.location.href, currentState()));
      }
    }

    function currentState() {
      if (!comparisonActive || !validateSelection()) return { pilot: isPilot2023 };
      return { topic: topicSelect.value, partyA: partyASelect.value,
        partyB: partyBSelect.value, pilot: isPilot2023 };
    }
    window.NeutralSharing.getState = currentState;
    function updateComparison() {
      comparisonActive = true;
      renderComparison();
      if (!validateSelection()) {
        window.history.replaceState({}, '', window.NeutralSharing.stableUrl(window.location.href, { pilot: isPilot2023 }));
      }
      const label = document.querySelector('#share-button span:last-child');
      if (label) label.textContent = validateSelection() ? 'Compartir esta comparación' : 'Compartir esta página';
    }

    // Attach form and select listeners
    topicSelect.addEventListener('change', updateComparison);
    partyASelect.addEventListener('change', updateComparison);
    partyBSelect.addEventListener('change', updateComparison);

    form.addEventListener('submit', function (evt) {
      evt.preventDefault();
      updateComparison();
      if (validateSelection() && measuresContainer && typeof measuresContainer.scrollIntoView === 'function') {
        measuresContainer.scrollIntoView({ behavior: 'auto', block: 'start' });
      }
    });

    let lastFocusedTrigger = null;

    function openManifestoModal(data) {
      let dialog = document.getElementById('manifesto-dialog');
      if (!dialog && typeof document.createElement === 'function' && document.body && typeof document.body.appendChild === 'function') {
        dialog = document.createElement('dialog');
        dialog.id = 'manifesto-dialog';
        dialog.className = 'manifesto-dialog';
        dialog.setAttribute('aria-labelledby', 'dialog-party-name');
        document.body.appendChild(dialog);
      }
      if (!dialog) return;

      let caveats = [];
      try {
        caveats = JSON.parse(data.caveats || '[]');
      } catch (e) {
        caveats = [];
      }

      let caveatsHtml = '';
      if (caveats.length > 0) {
        caveatsHtml = '<div class="dialog-caveats-box">' +
          '<h4 class="dialog-caveats-title">Condiciones y matices registrados en el programa:</h4>' +
          '<ul class="dialog-caveats-list">';
        for (let i = 0; i < caveats.length; i++) {
          caveatsHtml += '<li>' + escapeHtml(caveats[i]) + '</li>';
        }
        caveatsHtml += '</ul></div>';
      }

      let instrumentHtml = '';
      if (data.instrument) {
        instrumentHtml = '<div class="dialog-meta-item">' +
          '<span class="meta-label">Instrumento propuesto</span>' +
          '<span class="meta-value">' + escapeHtml(data.instrument) + '</span>' +
          '</div>';
      }

      const locatorText = data.section ? data.section : data.source;

      let externalPdfBtn = '';
      if (data.sourceUrl) {
        externalPdfBtn = '<a href="' + escapeHtml(data.sourceUrl) + '" target="_blank" rel="noopener noreferrer" class="btn-open-full-pdf">' +
          '<span aria-hidden="true">↗</span> ' +
          '<span>Abrir programa completo original en la web oficial (PDF)</span>' +
          '<span class="sr-only">(se abre en una ventana nueva)</span>' +
          '</a>';
      }

      dialog.innerHTML = '<div class="dialog-content">' +
        '<header class="dialog-header">' +
        '<div class="dialog-header-meta">' +
        '<span class="party-pill ' + escapeHtml(data.partyPillClass || 'party-pill-a') + '" aria-hidden="true">' + escapeHtml(data.partyPill || 'A') + '</span>' +
        '<div>' +
        '<span class="dialog-eyebrow">Visor de extracto del programa</span>' +
        '<h3 id="dialog-party-name" class="dialog-party-name">' + escapeHtml(data.partyName) + '</h3>' +
        '</div>' +
        '</div>' +
        '<button type="button" class="dialog-close-btn" id="dialog-close-btn" aria-label="Cerrar visor">✕</button>' +
        '</header>' +
        '<div class="dialog-body">' +
        '<div class="dialog-meta-bar">' +
        '<div class="dialog-meta-item">' +
        '<span class="meta-label">Documento oficial</span>' +
        '<span class="meta-value">' + escapeHtml(data.source) + '</span>' +
        '</div>' +
        instrumentHtml +
        '</div>' +
        '<div class="dialog-excerpt-card">' +
        '<div class="dialog-excerpt-header">' +
        '<span class="excerpt-badge">Cita textual verificada</span>' +
        '<span class="excerpt-locator">' + escapeHtml(locatorText) + '</span>' +
        '</div>' +
        '<blockquote class="dialog-quote">' +
        '<p>«' + escapeHtml(data.quote) + '»</p>' +
        '</blockquote>' +
        '</div>' +
        caveatsHtml +
        '<div class="dialog-legal-callout" role="note">' +
        '<span class="legal-icon" aria-hidden="true">ℹ</span>' +
        '<p><strong>Derecho de cita (art. 32.1 TRLPI):</strong> Fragmento reproducido literalmente para investigación y contraste cívico. La titularidad y explotación del programa corresponden a la formación política.</p>' +
        '</div>' +
        '</div>' +
        '<footer class="dialog-footer">' +
        externalPdfBtn +
        '<button type="button" class="btn-close-dialog" id="dialog-dismiss-btn">Cerrar visor</button>' +
        '</footer>' +
        '</div>';

      function closeDialog() {
        if (typeof dialog.close === 'function') {
          dialog.close();
        } else {
          dialog.removeAttribute('open');
        }
        if (lastFocusedTrigger && typeof lastFocusedTrigger.focus === 'function') {
          lastFocusedTrigger.focus();
        }
      }

      const closeBtn = dialog.querySelector('#dialog-close-btn');
      const dismissBtn = dialog.querySelector('#dialog-dismiss-btn');
      if (closeBtn) closeBtn.addEventListener('click', closeDialog);
      if (dismissBtn) dismissBtn.addEventListener('click', closeDialog);

      dialog.addEventListener('click', function (evt) {
        if (evt.target === dialog) {
          closeDialog();
        }
      });

      if (typeof dialog.showModal === 'function') {
        dialog.showModal();
      } else {
        dialog.setAttribute('open', '');
      }
    }

    if (measuresContainer) {
      measuresContainer.addEventListener('click', function (evt) {
        const btn = evt.target && evt.target.closest ? evt.target.closest('.btn-open-manifesto') : null;
        if (btn) {
          lastFocusedTrigger = btn;
          openManifestoModal({
            partyName: btn.getAttribute('data-party-name'),
            partyPill: btn.getAttribute('data-party-pill'),
            partyPillClass: btn.getAttribute('data-party-pill-class'),
            statusLabel: btn.getAttribute('data-status-label'),
            source: btn.getAttribute('data-source'),
            section: btn.getAttribute('data-section'),
            instrument: btn.getAttribute('data-instrument'),
            quote: btn.getAttribute('data-quote'),
            caveats: btn.getAttribute('data-caveats'),
            sourceUrl: btn.getAttribute('data-source-url')
          });
        }
      });
    }

    // Render defaults without converting home into a comparison URL.
    renderComparison();
    window.history.replaceState({}, '', window.NeutralSharing.stableUrl(window.location.href, currentState()));
    if (comparisonActive) document.querySelector('#share-button span:last-child').textContent = 'Compartir esta comparación';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
