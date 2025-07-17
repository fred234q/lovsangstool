// import ChordSheetJS from './bundle.js';
import * as ChordProjectParser from "https://cdn.jsdelivr.net/npm/chordproject-parser@1.0.4/+esm";
document.addEventListener('DOMContentLoaded', () => {
    const songId = document.querySelector('#lyrics-container').dataset.songId;
    parse_song(songId);
});

// Get new search results via metasearch in Python
// const queryString = window.location.search;
// const urlParams = new URLSearchParams(queryString);
// const query = urlParams.get('q')
// fetch(`/get-songs/${query}`)

function parse_song(songId) {

    fetch(`/sang/${songId}/chordpro`)
    .then(response => response.json())
    .then(chordproObject => {
        // Print song
        console.log(chordproObject)
        const chordproLyrics = chordproObject.chordpro

        const parser = new ChordProjectParser.default.ChordProParser();
        const song = parser.parse(chordproLyrics);

        const formatter = new ChordProjectParser.default.HtmlFormatter();
        const songText = formatter.format(song);

        document.querySelector('#lyrics-container').innerHTML = songText.join('');
    })
    .catch(error => {
        console.log('Error:', error);
    });


}

