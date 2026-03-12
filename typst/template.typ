// Pandoc helper definitions (blockquote, horizontalrule, endnote, etc.)
$definitions.typst()$

// Override the conf function for Tamil meditation books
#let conf(
  title: none,
  authors: none,
  date: none,
  abstract: none,
  cols: 1,
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2cm, right: 2cm),
  paper: "a4",
  lang: "ta",
  region: "IN",
  font: ("Noto Sans Tamil", "Noto Sans"),
  fontsize: 11pt,
  sectionnumbering: none,
  doc,
) = {
  set page(paper: paper, margin: margin, numbering: "1")
  set par(justify: true, leading: 0.8em)
  set text(lang: lang, region: region, font: font, size: fontsize)
  set heading(numbering: sectionnumbering)
  show link: set text(fill: rgb("#1a56db"))

  // Title page
  if title != none {
    align(center + horizon)[
      #text(weight: "bold", size: 24pt)[#title]
      #v(1em)
      #if authors != none {
        for author in authors {
          text(size: 14pt)[#author.name]
        }
      }
    ]
    pagebreak()
  }

  // Table of contents
  outline(depth: 3, indent: 1em)
  pagebreak()

  if cols == 1 { doc } else { columns(cols, doc) }
}

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
      affiliation: [],
      email: [] ),
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
  cols: $if(columns)$$columns$$else$1$endif$,
  doc,
)

$for(header-includes)$
$header-includes$

$endfor$
$for(include-before)$
$include-before$

$endfor$
$body$
