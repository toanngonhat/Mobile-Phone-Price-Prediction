\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hcmut-report}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[12pt,a4paper,oneside]{article}

\RequirePackage[utf8]{vntex,inputenc}
\RequirePackage{anyfontsize,amsmath,amssymb}
\RequirePackage[T5]{fontenc}

\RequirePackage{geometry,graphicx,indentfirst,setspace,titlesec}
\RequirePackage{tikz}
\usetikzlibrary{calc}
\RequirePackage{booktabs}
\RequirePackage{placeins}
\RequirePackage{flafter}
\RequirePackage[center]{caption}

\RequirePackage{fancyhdr,hyperref}
\RequirePackage[super,square,sort]{natbib}

% Change to '[english,vietnamese]' to use Vietnamese labels
\RequirePackage[english]{babel}

% Custom commands
\newcommand{\Month}{
  \ifcase \the\month
  \or Th\'ang 1
  \or Th\'ang 2
  \or Th\'ang 3
  \or Th\'ang 4
  \or Th\'ang 5
  \or Th\'ang 6
  \or Th\'ang 7
  \or Th\'ang 8
  \or Th\'ang 9
  \or Th\'ang 10
  \or Th\'ang 11
  \or Th\'ang 12
  \fi
}

\newcommand{\@upperuniname}{ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH}
\newcommand{\@uniname}{TRƯỜNG ĐẠI HỌC BÁCH KHOA}
\newcommand{\@fulluniname}{TRƯỜNG ĐẠI HỌC BÁCH KHOA - ĐẠI HỌC QUỐC GIA TP.HCM}


% Department name intentionally omitted from headers/cover.
% \deptname is kept for compatibility but unused.
\newcommand{\@deptname}{}
\newcommand{\deptname}[1]{\renewcommand{\@deptname}{#1}}

\newcommand{\@coursename}{Course name}
\newcommand{\coursename}[1]{\renewcommand{\@coursename}{#1}}

\newcommand{\@reporttype}{Assignment Report}
\newcommand{\reporttype}[1]{\renewcommand{\@reporttype}{#1}}

\renewcommand{\@title}{Report title}

\newcommand{\@advisor}{Advisor}
\newcommand{\advisor}[1]{\renewcommand{\@advisor}{#1}}

\newcommand{\@stuname}{STUDENT:\ H (xxxxxxx)}
\newcommand{\stuname}[1]{\renewcommand{\@stuname}{#1}}

\newcommand{\@reportplace}{Thành phố Hồ Chí Minh}
\newcommand{\reportplace}[1]{\renewcommand{\@reportplace}{#1}}

\newcommand{\@reporttime}{\Month \the\year}
\newcommand{\reporttime}[1]{\renewcommand{\@reporttime}{#1}}

% Configurations
%\graphicspath{{subdir1/}{subdir2/}{subdir3/}...{subdirn/}}

\geometry{
  paper=a4paper,
  left=2.5cm,
  right=2.5cm,
  vmargin=2cm,
  includeheadfoot=true,
  headheight=2pt,
  bindingoffset=0pt,
  twoside=false
}

\setstretch{1.15}
\AtBeginDocument{%
  \titlespacing*{\section}{0pt}{1.15pt}{1.15pt}%
  \titlespacing*{\subsection}{0pt}{1.15pt}{1.15pt}%
  \titlespacing*{\subsubsection}{0pt}{1.15pt}{1.15pt}%

}
\raggedbottom
\renewcommand{\arraystretch}{1.2}

% Set depth of numbering for sections and table of contents
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}

% Set depth of numbering for counters
\AtBeginDocument{\counterwithin{equation}{section}}
\AtBeginDocument{\counterwithin{table}{section}}
\AtBeginDocument{\counterwithin{figure}{section}}

\AtBeginDocument{%
  \renewcommand*\bibname{Tài liệu tham khảo}%
  \renewcommand*\refname{Tài liệu tham khảo}%
}

\hypersetup{
  colorlinks=true,
  linkcolor=black,
  citecolor=red,
  urlcolor=blue
}

\renewcommand{\headrulewidth}{0.3pt}
% Lower the header rule slightly to avoid logo overlap
\renewcommand{\headrule}{%
  \vspace{5.0pt}%
  \hrule\@height\headrulewidth\@width\headwidth%
  \vspace{0pt}%
}
\renewcommand{\footrulewidth}{0pt}

\pagestyle{fancy}
\fancyhf{}

%\renewcommand{\subsectionmark}[1]{\markright{\thesubsection.\ #1}}

% The drawing units are interpreted as multiples of \unitlength
% unless a unit is given
%\setlength{\unitlength}{1pt}

\if@twoside
  \fancyhead[EL]{
    \bfseries
    \begin{tabular}{rl}
      \begin{picture}(25pt,15pt)
        \put(0,-8pt){\includegraphics[width=20pt]{graphics/hcmut.png}}
      \end{picture}
      \begin{tabular}{l}
        \ttfamily\@fulluniname \\
      \end{tabular}
    \end{tabular}
  }
  \fancyhead[OR]{
    \bfseries
    \begin{tabular}{rl}
      \begin{tabular}{r}
        \ttfamily\@fulluniname \\
      \end{tabular}
      \begin{picture}(25pt,15pt)
        \put(0,-8pt){\includegraphics[width=20pt]{graphics/hcmut.png}}
      \end{picture}
    \end{tabular}
  }
\else
  \fancyhead[R]{
    \bfseries
    \begin{tabular}{rl}
      \begin{tabular}{r}
        \ttfamily\@fulluniname \\
      \end{tabular}
      \begin{picture}(25pt,15pt)
        \put(0,-8pt){\includegraphics[width=20pt]{graphics/hcmut.png}}
      \end{picture}
    \end{tabular}
  }
\fi

\fancyfoot[C]{\thepage}

% Custom pages and sections
\newcommand{\coverpage}{
  \pagestyle{empty}
  \begin{titlepage}
    \begin{tikzpicture}[remember picture, overlay]
      \draw[line width=4pt]
        ($(current page.north west) + (0.4in,-0.5in)$)
        rectangle
        ($(current page.south east) + (-0.4in,0.5in)$);
      \draw[line width=1.5pt]
        ($(current page.north west) + (0.45in,-0.55in)$)
        rectangle
        ($(current page.south east) + (-0.45in,0.55in)$);
    \end{tikzpicture}

    \vspace*{-1.0cm}
    \begin{center}
      {\large\textbf{\MakeUppercase{\@upperuniname}}} \\
      \vspace{0.05cm}
      {\large\textbf{\MakeUppercase{\@uniname}}} \\
      \vspace{0.05cm}
      {\large\textbf{\MakeUppercase{\@deptname}}}
    \end{center}

    \vspace{0.3cm}

    \begin{center}
      \includegraphics[width=3.5cm]{graphics/hcmut.png}
    \end{center}

    \begin{center}
      {\Large\textbf{\@reporttype}}\par
      \vspace{0.2cm}
      {\Large\textbf{\@coursename}}\par
      \vspace{0.4cm}
      {\Large\textbf{\@title}}\par
    \end{center}

    \vspace{0.5cm}
    \begin{center}
      \mdseries
      \begin{tabular}{l l l}
        {\normalsize Giảng viên hướng dẫn:} \@advisor \\
        {\normalsize Học viên:} & & \\
        \@stuname
      \end{tabular}
    \end{center}

    \vfill
    \begin{center}
      {\normalsize \MakeUppercase{\@reportplace}, \@reporttime}
    \end{center}
  \end{titlepage}

  \cleardoublepage
  \pagestyle{fancy}
}
