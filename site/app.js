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
        '<span>Leer extracto en la app</span>' +
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
        const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        measuresContainer.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth', block: 'start' });
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
