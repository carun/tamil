// Pandoc helper definitions
#let blockquote(body) = [
  #set text(size: 0.92em)
  #block(inset: (left: 1.5em, top: 0.2em, bottom: 0.2em))[#body]
]

#let horizontalrule = line(start: (25%,0%), end: (75%,0%))

#let endnote(num, contents) = [
  #stack(dir: ltr, spacing: 3pt, super[#num], contents)
]

#show terms.item: it => block(breakable: false)[
  #text(weight: "bold")[#it.term]
  #block(inset: (left: 1.5em, top: -0.4em))[#it.description]
]

#set table(inset: 6pt, stroke: none)

#show figure.where(kind: table): set figure.caption(position: top)
#show figure.where(kind: image): set figure.caption(position: bottom)

// LaTeX Computer Modern style — matching Mahaparinirvana Sutra PDF layout
#let conf(
  title: none,
  authors: none,
  date: none,
  abstract: none,
  cols: 1,
  margin: (top: 2.0cm, bottom: 2.54cm, left: 2.54cm, right: 2.54cm),
  paper: "a4",
  lang: "ta",
  region: "IN",
  font: ("New Computer Modern", "Noto Sans Tamil"),
  fontsize: 10.91pt,
  
  sectionnumbering: none,
  pagenumbering: "1",
  doc,
) = {
  set page(
    paper: paper,
    margin: margin,
    numbering: pagenumbering,
    number-align: center + bottom,
    // Running header with book title in italics (right-aligned on even, left on odd)
    header: context {
      if counter(page).get().first() > 0 {
        set text(size: 0.9em)
        align(center)[
          #line(length: 100%, stroke: 0.4pt)
        ]
      }
    },
  )

  // Body text: 10.91pt, 13.15pt leading (1.205× ratio), first-line indent
  set par(justify: true, leading: 0.6em, first-line-indent: 1.5em)
  set text(lang: lang, region: region, font: font, size: fontsize)
  set heading(numbering: sectionnumbering)

  // Chapter headings — 17pt bold, large spacing
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    block(above: 3em, below: 1.5em)[
      #set text(size: 17.2pt, weight: "bold")
      #it.body
    ]
    // No indent on first paragraph after heading
    par(first-line-indent: 0pt, [])
  }

  // Section headings — 14.3pt bold
  show heading.where(level: 2): it => {
    block(above: 2em, below: 1em)[
      #set text(size: 14.3pt, weight: "bold")
      #it.body
    ]
    par(first-line-indent: 0pt, [])
  }

  // Subsection headings — 12pt bold
  show heading.where(level: 3): it => {
    block(above: 1.5em, below: 0.8em)[
      #set text(size: 12pt, weight: "bold")
      #it.body
    ]
    par(first-line-indent: 0pt, [])
  }

  // Title page — no page number
  if title != none {
    page(numbering: none, header: none)[
      #v(1fr)
      #align(center)[
        #text(weight: "bold", size: 20.7pt)[#title]
        #v(0.3em)
        #line(length: 100%, stroke: 1pt)
        #v(1.5em)
        #if authors != none {
          for author in authors {
            text(size: 12pt)[#author.name]
          }
        }
      ]
      #v(2fr)
    ]
  }

  // Table of contents — roman numerals, no header
  page(numbering: "i", header: none)[
    #set text(size: 11.96pt)
    #outline(depth: 3, indent: 1.5em, title: none)
  ]

  if cols == 1 { doc } else { columns(cols, doc) }
}

#set smartquote(enabled: false)

$for(header-includes)$
$header-includes$

$endfor$
#show: doc => conf(
$if(title)$
  title: [$title$],
$endif$
$if(author)$
  authors: (
$for(author)$
$if(author.name)$
    ( name: [$author.name$],
      affiliation: [$author.affiliation$],
      email: [$author.email$] ),
$else$
    ( name: [$author$],
      affiliation: "",
      email: "" ),
$endif$
$endfor$
    ),
$endif$
$if(lang)$
  lang: "$lang$",
$endif$
$if(papersize)$
  paper: "$papersize$",
$endif$
$if(mainfont)$
  font: ("$mainfont$",),
$endif$
$if(fontsize)$
  fontsize: $fontsize$,
$endif$
  pagenumbering: $if(page-numbering)$"$page-numbering$"$else$"1"$endif$,
  cols: $if(columns)$$columns$$else$1$endif$,
  doc,
)

$for(include-before)$
$include-before$

$endfor$
$body$
