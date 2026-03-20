function capitalizeWords(sentence: string): string {
    const words = sentence.split(" ");
    const capitalizedWords = words.map(word => {
        const firstLetter = word.charAt(0).toUpperCase();
        const restOfWord = word.slice(1);
        return firstLetter + restOfWord;
    });

    return capitalizedWords.join(" ");
}

export { capitalizeWords };