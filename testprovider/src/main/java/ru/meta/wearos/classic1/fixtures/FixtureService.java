package ru.meta.wearos.classic1.fixtures;

import android.graphics.drawable.Icon;
import android.os.RemoteException;
import androidx.wear.watchface.complications.data.*;
import androidx.wear.watchface.complications.datasource.*;

/** Emulator-only fixture. Never packaged into the production watchface. */
public abstract class FixtureService extends ComplicationDataSourceService {
    protected abstract String title();
    protected abstract String value();
    private PlainComplicationText plain(String value) { return new PlainComplicationText.Builder(value).build(); }
    private ComplicationData data(ComplicationType type) {
        boolean titleless = getSharedPreferences("fixture",0).getBoolean("titleless",false);
        if(type==ComplicationType.RANGED_VALUE) {
            RangedValueComplicationData.Builder ranged = new RangedValueComplicationData.Builder(Float.parseFloat(value()),0f,250f,plain("TEST RANGE "+title()));
            if (!titleless) ranged.setTitle(plain(title()));
            return ranged.build();
        }
        ShortTextComplicationData.Builder builder = new ShortTextComplicationData.Builder(plain(value()), plain("TEST DATA: " + title() + " " + value()));
        if (!titleless) builder.setTitle(plain(title()));
        if (this instanceof Weather) builder.setMonochromaticImage(new MonochromaticImage.Builder(Icon.createWithResource(this, R.drawable.rain)).build());
        return builder.build();
    }
    @Override public void onComplicationRequest(ComplicationRequest request, ComplicationRequestListener listener) {
        try { listener.onComplicationData(data(request.getComplicationType())); } catch (RemoteException error) { throw new RuntimeException(error); }
    }
    @Override public ComplicationData getPreviewData(ComplicationType type) { return data(type); }
    public static class Heart extends FixtureService { private boolean alternate(){return getSharedPreferences("fixture",0).getBoolean("alternate",false);}
 protected String title(){return getSharedPreferences("fixture",0).getBoolean("unknown_long_title",false)?"ПРОИЗВОЛЬНЫЙ ПОКАЗАТЕЛЬ НОВОГО ПРИЛОЖЕНИЯ":getSharedPreferences("fixture",0).getBoolean("long_title",false)?"МАКСИМАЛЬНАЯ ВЫСОТА НАД УРОВНЕМ МОРЯ":alternate()?"ВЫСОТА":"ПУЛЬС";} protected String value(){return alternate()?"182":"72";} }
    public static class Weather extends FixtureService { private boolean swapped(){return getSharedPreferences("fixture",0).getBoolean("weather_swapped",false);}
 protected String title(){return swapped()?"+4°C":"ПОГОДА";} protected String value(){return swapped()?"ТЕСТ ГОРОД":"+4°C";} }
    public static class Floors extends FixtureService { protected String title(){return "ЭТАЖИ";} protected String value(){return "9";} }
    public static class Battery extends FixtureService { protected String title(){return "ЗАРЯД";} protected String value(){return "82%";} }
    public static class Steps extends FixtureService { protected String title(){return "ШАГИ";} protected String value(){return "10 780";} }
}
