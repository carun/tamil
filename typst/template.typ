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

// Tamil meditation books conf function
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
  pagenumbering: "1",
  doc,
) = {
  set page(paper: paper, margin: margin, numbering: pagenumbering)
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
