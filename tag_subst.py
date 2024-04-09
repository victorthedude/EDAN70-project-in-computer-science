import re

def __html_refs_repl(m):
    ref = m.group(4)
    match ref:
        case '&quot;':
            return '""'
        case '&ndash;':
            return '-'
        case '&rsquo;':
            return "'"
        case '&amp;':
            return '&'
        case '&nbsp;':
            return ' '
        case '&lt;':
            return '<'
        case '&gt;':
            return '>'
        case _:
            return ref

def __html_tags_repl(m):
    tag = m.group(1)
    content = m.group(3)
    match tag:
        case 'b' | 'i': 
            return m.group(0) # preserve stylization
        case 'sup' | 'sub' | 'small' | 'span': #  'span class="sp"'
            return content # remove tags, keep text
        case 'table':
            tag_attr = m.group(2)
            match tag_attr:
                case 'class="ic"' | 'class="il"' | 'class="ir"' | 'class="b"':
                    return '' # broken images, remove
                case _:
                    return content
        case 'tr':
            return subst_HTML_tags(content) # recursively remove <tr> and <td> tags in a <table>
        case 'td': # remove tag but keep content
            return subst_HTML_tags(content)
        case _:
            single_tag = m.group(5)
            match single_tag:
                case 'table' | 'tr' | 'td':
                    return ""
                case 'b' | 'i': # sometimes, stylization spans several lines which regex will not otherwise detect
                    return m.group(0)
            return content

def __tags_repl(m):
    if m.group(0) == '<br>':   # remove HTML line breaks found at the beginning of each line
        return ""
    elif m.group(0)[0] == '<': # if HTML tag
        return __html_tags_repl(m)
    elif m.group(0)[0] == '&': # if HTML character code
        return __html_refs_repl(m)
    return ""

def subst_HTML_tags(HTML_content):
    tag_pattern = r'<br>|<([^>\s]+)\s?([^>]*)>(.*?)<\/\1>|(&[^&;]*;)|<\/?([^>\s]+)>'
    return re.sub(tag_pattern, __tags_repl, HTML_content)

if __name__ == "__main__":
    test = """
    <b>Anomali,</b> <i>astron.,</i> namn på vissa vinklar, som angifva
    en planets läge i hans bana. <i>Sann anomali</i> är den
    vinkel, från perihelium räknad, som radius vector
    bildar med &quot;apsidlinien&quot;. Då en planet rör sig med
    olika hastighet i olika delar af sin elliptiska
    bana, så följer deraf, att sanna anomalien ej växer
    lika mycket på lika <sub>tidsintervaller.</sub> <i>Medelanomali</i>
    kallas den vinkel, som radius vector skulle bilda
    med apsidlinien, om <sup>planeten</sup> tänktes röra sig i
    cirkelbana med en diameter lika med apsidlinien och
    med en sådan likformig hastighet, att omloppstiderna
    i cirkeln och ellipsen vore lika. 

    <table class="il"><tr><td style="text-align: center;"><a href="javascript:ShowPopUp(1)"><img src="/img/broken.png" alt="illustration placeholder" title="illustration placeholder"></a></td></tr><tr><td> </tr></table>

    Medelanomalien växer alltså proportionelt mot tiden. Den likformiga
    rörelsen benämnes medelrörelse. <span class="sp">Anomalistiskt år</span>,
    se <span class="sp">Astronomiskt år</span>. J. O. B.

    <table>
    <tr><td>Sulphas calcicus     </td><td style="text-align: right;">0,022.</td></tr>
    <tr><td>Chloretum calcicum   </td><td style="text-align: right;">0,143.</td></tr>
    <tr><td>Chloret. kalicum     </td><td style="text-align: right;">0,046.</td></tr>
    <tr><td>Chloret. natricum    </td><td style="text-align: right;">0,449.</td></tr>
    <tr><td>Chloret. magnesium   </td><td style="text-align: right;">0,067.</td></tr>
    <tr><td>Chloret. ammonicum   </td><td style="text-align: right;">0,076.</td></tr>
    <tr><td>Chloret. ferrosum    </td><td style="text-align: right;">0,070.</td></tr>
    <tr><td>Carbon. ferrosus     </td><td style="text-align: right;">1,027.</td></tr>
    <tr><td>Phosphas aluminicus  </td><td style="text-align: right;">0,009.</td></tr>
    <tr><td>Acidum silicicum     </td><td style="text-align: right;">0,217.</td></tr>
    <tr><td>Materia organica     </td><td style="text-align: right;">0,277.</td></tr>
    <tr><td></td><td style="text-align: right;">Summa 2,435.</td></tr>
    </table>

    <table>
    <tr><td></td><td>Celt fr.Downs</td><td COLSPAN=2> Bronsringar ifrån en gallisk-romersk graf.</td></tr>
    <tr><td>Koppar </td><td style="text-align: center;">85,23 </td><td style="text-align: center;">75,55 </td><td style="text-align: center;">79,93</td></tr>
    <tr><td>Tenn   </td><td style="text-align: center;">13,11 </td><td style="text-align: center;">23,52 </td><td style="text-align: center;">15,73</td></tr>
    <tr><td>Bly    </td><td style="text-align: center;"> 1,14 </td><td style="text-align: center;"> 0,47 </td><td style="text-align: center;"> 3,50</td></tr>
    <tr><td> </td><td>Mynt frånAlexanderden stores tid.</td><td>Romerskt as
    år 500 f. Kr.</td><td>Mynt frånAlexanderSeveri tid.</td></tr>
    <tr><td>Koppar </td><td style="text-align: center;">95,96 </td><td style="text-align: center;">69,69 </td><td style="text-align: center;">89,0</td></tr>
    <tr><td>Tenn   </td><td style="text-align: center;"> 3,28 </td><td style="text-align: center;"> 7,16 </td><td style="text-align: center;">10,2</td></tr>
    <tr><td>Bly    </td><td style="text-align: center;"> 0,76 </td><td style="text-align: center;">21,82 </td><td style="text-align: center;"> 0,8</td></tr>
    </table>
    """

    test2= """"
    <i>Allgemeine zoologie</i> (1850), <i>Geschichte der natur</i>
    <br>(1841&ndash;49) och <i>Untersuchungen über die
    <br>entwickelungsgesetze der organischen welt während der
    <br>bildungszeit unserer erdoberfläche</i> (1858;
    <br>prisbelönt af Franska vetenskapsakademien). I det
    <br>stora verket &quot;Neue encyklopädie für
    <br>wissenschaften und künste&quot; bearbetade han den zoologiske
    <br>delen (1850). Af största vigt är hans <i>Klassen
    <br>und ordnungen des thierreichs, wissenschaftlich
    <br>dargestellt in wort und bild</i> (1859 o. f.;
    <br>fortsatt af Keferstein, Gerstäcker m. fl.). Ifrån 1830
    <br>utgaf B. jämte Leonhard tidskriften &quot;Jahrbuch
    <br>für mineralogie, geognosie, geologie und
    <br>petrefaktenkunde&quot;.
    <br>
    <br><b>Bronner,</b> <span class="sp">Johann Philipp,</span> tysk vinodlare,
    <br>f. 1792, d. 1865, offentliggjorde 1825 den s. k.
    <br>bocksnittsmetoden för vinstockars uppdragande
    <br>samt utgaf flere skrifter angående vinodling.
    <br>I sina vinplanteringar uppdrog han omkr. 400
    <br>drufsorter, från åtskilliga delar af Europa.
    <br>
    <br><b>Brons</b> (af Ital. <i>bronzo,</i> malm, troligen af
    <br>Grek. <i>bronte,</i> åska), <i>kem.,</i> en legering af koppar
    <br>och tenn, stundom med tillsatser af bly och
    <br>zink. Sedan uråldriga tider har denne metall
    <br>varit använd till mynt, prydnader och vapen
    <br>m. m. Sammansättningen af antik brons synes
    <br>af nedanstående analyser:
    <table>
    <tr><td></td><td>Celt fr.<br>Downs</td><td COLSPAN=2> Bronsringar ifrån en gallisk-<br>romersk graf.</td></tr>
    <tr><td>Koppar </td><td style="text-align: center;">85,23 </td><td style="text-align: center;">75,55 </td><td style="text-align: center;">79,93</td></tr>
    <tr><td>Tenn   </td><td style="text-align: center;">13,11 </td><td style="text-align: center;">23,52 </td><td style="text-align: center;">15,73</td></tr>
    <tr><td>Bly    </td><td style="text-align: center;"> 1,14 </td><td style="text-align: center;"> 0,47 </td><td style="text-align: center;"> 3,50</td></tr>
    <tr><td> </td><td>Mynt från<br>Alexander<br>den stores tid.</td><td>Romerskt as<br>
    <br>år 500 f. Kr.</td><td>Mynt från<br>Alexander<br>Severi tid.</td></tr>
    <tr><td>Koppar </td><td style="text-align: center;">95,96 </td><td style="text-align: center;">69,69 </td><td style="text-align: center;">89,0</td></tr>
    <tr><td>Tenn   </td><td style="text-align: center;"> 3,28 </td><td style="text-align: center;"> 7,16 </td><td style="text-align: center;">10,2</td></tr>
    <tr><td>Bly    </td><td style="text-align: center;"> 0,76 </td><td style="text-align: center;">21,82 </td><td style="text-align: center;"> 0,8</td></tr>
    </table>
    <br>
    <br>En sammanställning af analyser af antik brons
    <br>finnes i Gmelin-Krauts &quot;Handbuch der
    <br>anorganischen chemie&quot; (6:te uppl., III b., 725 s.). &ndash; F. n.
    <br>nyttjas brons af olika sammansättning till olika
    <br>ändamål. Kanonmetall innehåller 9&ndash;10 proc.
    <br>tenn; malm eller klockmetall 20&ndash;25;
    <br>medaljbrons 5&ndash;10: statybrons innehåller 2,5&ndash;4 proc.
    <br>tenn och 11&ndash;17 proc. zink. Den svenske
    <br>myntmetallen, hvaraf öreslantar slås, består af 95
    <br>proc. koppar, 4 proc. tenn och 1 proc. zink.
    <br>Brons är i allmänhet en hård metall, som genom
    <br>upphettning och hastig afkylning blir smidbar
    <br>och kan präglas. Efter upphettning och
    <br>långsam afsvalning blir han åter till en viss grad
    <br>spröd. I fuktig luft öfverdrages han med en
    <br>grön hinna eller, skorpa (patina), som skyddar
    <br>underliggande metallpartier och meddelar
    <br>bronsstatyer en angenäm färg. Ett sådant öfverdrag
    <br>kan utan svårighet framkallas genom
    <br>bestrykning med en lösning af salmiak och oxalsyra
    <br>i ättiksyra. P. T. C.
    <br>
    <br><b>Bronsera,</b> med bronsfärger bestryka föremål
    <br>af gips, trä, metall e. d. &ndash; Subst.
    <br><span class="sp">Bronsering</span>. P. T. C.
    <br>
    <br><b>Bronsfärger</b> l. <span class="sp">Bronspulver,</span> <i>tekn.,</i>
    <br>legeringar af koppar och zink, som utvalsats till
    <br>tunna blad och efter fuktning med vatten eller
    <br>honinglösning sönderrifvits till pulver. P. T. C.
    <br>
    <br><b>Bronsgjutning,</b> en teknisk konst, känd redan
    <br>i den förhistoriska tiden, består i danandet af
    <br>
    <br>föremål af smält brons. Den förnämsta branchen
    <br>i denna teknik är staty- eller konstgjutningen,
    <br>som sker efter konstnärligt utförda modeller och
    <br>har till uppgift att troget återgifva originalen.
    <br>Bildstoder äro alltid ihåliga och gjutas vanligen
    <br>i flere stycken. Fordom skedde gjutningen på
    <br>följande sätt. Till en början förfärdigades en
    <br>af gips, tegelmjöl och fet lera bestående <span class="sp">kärna,</span>
    <br>hvilken i förminskad skala någorlunda återgaf
    <br>det blifvande konstverket. Denna kärna
    <br>öfverdrogs med ett vaxlager af samma tjocklek som
    <br>bronsgodset skulle erhålla, och sedan
    <br>utarbetade konstnären modellen fullständigt i
    <br>vaxbetäckningen. Derefter öfverdrogs vaxet ytterst
    <br>försigtigt med ett starkt lager af fin slammad
    <br>lera, hvilket sedan öfverdrogs med ett lager af
    <br>gröfre lera. Dessa båda lager bildade den s. k.
    <br><span class="sp">manteln</span>. Sedan denna blifvit förstärkt med
    <br>jernstänger och jernband, upphettades
    <br>gjutformen, så att leran torkade, på samma gång
    <br>som vaxet smälte och bortrann genom
    <br>öppningar i manteln. Genom vaxets bortskaffande
    <br>bildades emellan manteln och kärnan ett tom-
    <br>rum, som bronsen skulle fylla. Kärnan stod
    <br>sålunda alldeles fri, med undantag af några
    <br>jernstänger, som från henne sköto ut genom manteln.
    <br>Sedan den ingjutne bronsen hunnit svalna,
    <br>sönderslogs formen; jernstängerna afsågades, och
    <br>figuren ciselerades. Detta gjutningssätt, hvilket
    <br>sannolikt begagnades redan af grekerna, var
    <br>emellertid förknippadt med flere olägenheter.
    <br>Nu användes derför ett annat sätt för
    <br>formningen, hvilken sker i motsatt riktning mot förut.
    <br>Metoden dervid är följande. Af
    <br>originalmodellen, som utföres i gips och i hel storlek på
    <br>en jernställning, tages en tjock ihålig
    <br>gipsafgjutning, i så många stycken som bildens storlek
    <br>kräfver. Dessa stycken beläggas invändigt med
    <br>modellvax af samma tjocklek, som metallen
    <br>kommer att få, hvarefter styckena
    <br>sammanfogas öfver kärnans af jernstänger
    <br>sammanhållne stomme. Under sammanfogningen,
    <br>hvilken sker nedifrån och uppåt, fylles håligheten
    <br>mellan vaxet och kärnstommen med ett af
    <br>gipspulver, sand, tegelmjöl och vatten hoprördt
    <br>bruk, hvilket snart hårdnar. Detta bildar sedan
    <br>kärnans hufvudmassa. När den yttre
    <br>gipsformen blifvit aftagen, förses vaxbilden på alla
    <br>framspringande punkter med två system af
    <br>vaxkanaler, hvilka samla sig i tjockare grenar
    <br>uppåt. Det ena af dessa system är afsedt
    <br>att insläppa den smälte metallen, det andra att
    <br>utsläppa luften. Den sålunda utrustade
    <br>vaxmodellen förses &ndash; på förut beskrifvet sätt &ndash;
    <br>med en mantel af eldfast formmassa
    <br>(ytterligare stärkt med ett murverk af rå tegelsten),
    <br>hvarefter det hela, sedan vaxet blifvit smält
    <br>och bortrunnit genom särskilda kanaler,
    <br>nedhissas i den framför gjutugnen befintliga
    <br>gjutgrafven. Sedan gjutformen blifvit från ugnen
    <br>fylld med den smälte metallen och denne hunnit
    <br>svalna, sönderslås manteln, och konstverket
    <br>upphissas för att ciseleras och afputsas. &ndash; En tredje
    <br>metod består deruti, att originalmodellen
    <br>afformas i ett eldfast ämne, hvarigenom en mantel
    <br>erhålles. Sedan denne, till förhindrande af
    <br>fastklibbning, invändigt öfverdragits med olja eller
    <br>
    <br>
    <br>
    """

    print(subst_HTML_tags(test2))