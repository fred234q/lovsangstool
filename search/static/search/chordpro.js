import ChordSheetJS from './bundle.js';

const chordSheet = ``.substring(1);

const parser = new ChordSheetJS.ChordProParser();
const song = parser.parse(chordSheet);

const formatter = new ChordSheetJS.HtmlDivFormatter();
const disp = formatter.format(song);
console.log(disp)

const lyrics = document.querySelector('#lyrics');
lyrics.innerHTML = disp;


const lyricsContainer = document.getElementById('lyrics');
const paragraphs = lyricsContainer.querySelectorAll('.paragraph');

// First hide all chords (CSS alternative)
const style = document.createElement('style');
style.textContent = '.chord { display: none !important; }';
document.head.appendChild(style);

// Process each paragraph
paragraphs.forEach(paragraph => {
    const rows = paragraph.querySelectorAll('.row');
    let formattedParagraph = document.createElement('div');
    formattedParagraph.className = 'lyrics-paragraph';

    rows.forEach(row => {
        // Handle section headers (like "Vers 1")
        if (row.querySelector('.comment')) {
            const header = document.createElement('div');
            header.className = 'section-header';
            header.textContent = row.querySelector('.comment').textContent;
            formattedParagraph.appendChild(header);
            return;
        }

        // Process lyric lines
        const lineDiv = document.createElement('div');
        lineDiv.className = 'lyric-line';
        
        const columns = row.querySelectorAll('.column');
        let lineText = '';
        
        columns.forEach(column => {
            const lyric = column.querySelector('.lyrics')?.textContent || '';
            lineText += lyric;
        });

        lineDiv.textContent = lineText.trim();
        if (lineText.trim()) {
            formattedParagraph.appendChild(lineDiv);
        }
    });

    paragraph.replaceWith(formattedParagraph);
});

// Clean up empty paragraphs
document.querySelectorAll('div').forEach(el => {
    if (!el.textContent.trim() && !el.children.length) {
        el.remove();
    }
});