import {getEmbedsu} from "./controllers/providers/EmbedSu/embedsu.js";
import {getTwoEmbed} from "./controllers/providers/2Embed/2embed.js";
import {getAutoembed} from "./controllers/providers/AutoEmbed/autoembed.js";
import {getPrimewire} from "./controllers/providers/PrimeWire/primewire.js";
import {getVidSrcCC} from "./controllers/providers/VidSrcCC/vidsrccc.js";
import {getVidSrc} from "./controllers/providers/VidSrc/VidSrc.js";
import {getVidSrcSu} from "./controllers/providers/VidSrcSu/VidSrcSu.js";
import {getVidSrcVip} from "./controllers/providers/VidSrcVip/VidSrcVip.js";
import {getXprime} from "./controllers/providers/xprime/xprime.js";
import {ErrorObject} from "./helpers/ErrorObject.js";
import {getVidsrcWtf} from "./controllers/providers/VidSrcWtf/VidSrcWtf.js";

const shouldDebug = process.argv.includes("--debug");

// --- دوال مساعدة لتحديد جودة الرابط ---

// دالة للتحقق من الرابط المفضل (الذهبي)
const isPreferredLink = (file) => {
    return file?.file?.includes('premilkyway.com') && file?.file?.includes('/hls2/');
};

// دالة للتحقق من أي رابط صالح كخطة بديلة
const isAnyValidLink = (file) => {
    return file && file.file && typeof file.file === 'string' && file.file.startsWith('http');
};


export async function scrapeMedia(media) {
    // قائمة موحدة للمزودين، مع وضع المصدر المفضل في البداية لزيادة احتمالية العثور عليه بسرعة
    const providers = [
        {fn: () => getTwoEmbed(media), name: "2Embed"},       // المصدر الأكثر احتمالاً للرابط المفضل
        {fn: () => getEmbedsu(media), name: "Embedsu"},
        {fn: () => getVidsrcWtf(media), name: "VidsrcWtf"},
        {fn: () => getAutoembed(media), name: "AutoEmbed"},
        {fn: () => getVidSrcSu(media), name: "VidSrcSu"},
        {fn: () => getVidSrcVip(media), name: "VidSrcVip"},
        {fn: () => getXprime(media), name: "Xprime"},
        {fn: () => getVidSrc(media), name: "VidSrc"},
        {fn: () => getPrimewire(media), name: "Primewire"},
        {fn: () => getVidSrcCC(media), name: "VidSrcCC"}, // معطل
    ];

    const errors = [];
    let fallbackResult = null; // لتخزين أول نتيجة صالحة كخطة بديلة

    for (const provider of providers) {
        try {
            if (shouldDebug) console.log(`[+] Trying provider: ${provider.name}`);
            
            const result = await provider.fn();

            if (result && !(result instanceof Error) && !(result instanceof ErrorObject)) {
                const filesArray = Array.isArray(result.files) ? result.files : (result.files ? [result.files] : []);
                
                // --- الهدف الأساسي: البحث عن الرابط المفضل ---
                const preferredFile = filesArray.find(isPreferredLink);
                if (preferredFile) {
                    if (shouldDebug) console.log(`[✔] Success! Found PREFERRED link from: ${provider.name}`);
                    const subtitles = Array.isArray(result.subtitles) ? result.subtitles.filter(Boolean) : [];
                    return { files: [preferredFile], subtitles, ...(shouldDebug && { errors }) };
                }

                // --- الخطة البديلة: إذا لم يتم العثور على الرابط المفضل، خزّن أول رابط صالح ---
                if (!fallbackResult) {
                    const anyValidFile = filesArray.find(isAnyValidLink);
                    if (anyValidFile) {
                        if (shouldDebug) console.log(`[*] Found a FALLBACK link from ${provider.name}. Storing it and continuing search for preferred link.`);
                        const subtitles = Array.isArray(result.subtitles) ? result.subtitles.filter(Boolean) : [];
                        fallbackResult = {
                            files: [anyValidFile],
                            subtitles: subtitles,
                            ...(shouldDebug && { errors })
                        };
                    }
                }
            } else if (result instanceof Error || result instanceof ErrorObject) {
                if (shouldDebug) errors.push({ provider: provider.name, error: result });
            }
        } catch (e) {
            if (shouldDebug) {
                errors.push({ provider: provider.name, error: new ErrorObject(e.message, provider.name, 500, e.stack, false, true) });
            }
        }
    }

    // إذا انتهت الحلقة دون العثور على الرابط المفضل، قم بإرجاع الخطة البديلة إن وجدت
    if (fallbackResult) {
        if (shouldDebug) console.log(`[-] Preferred link not found after all attempts. Returning the stored FALLBACK link.`);
        return fallbackResult;
    }

    // إذا فشلت جميع المحاولات
    if (shouldDebug) {
        console.log(`[-] All providers failed to return any valid links.`);
        errors.forEach(({ provider, error }) => console.error(`--- Error from ${provider} ---\n${error.toString()}`));
    }
    
    return { files: [], subtitles: [], ...(shouldDebug && { errors: errors.map(e => e.error) }) };
}