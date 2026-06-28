import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// CivicFlow App Theme
/// Material 3 design system matching the React frontend's design language.
/// Off-white workspace, clean cards, professional government SaaS aesthetic.
class AppTheme {
  AppTheme._();

  // ─── Colour Palette ───────────────────────────────────────────────────────
  static const Color background = Color(0xFFF9FAFB);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color border = Color(0xFFE5E7EB);

  static const Color textPrimary = Color(0xFF1E293B);   // slate-800
  static const Color textSecondary = Color(0xFF64748B); // slate-500
  static const Color textTertiary = Color(0xFF94A3B8);  // slate-400

  static const Color accent = Color(0xFF2563EB);        // blue-600
  static const Color accentLight = Color(0xFFEFF6FF);   // blue-50

  static const Color success = Color(0xFF16A34A);
  static const Color successLight = Color(0xFFF0FDF4);
  static const Color warning = Color(0xFFD97706);
  static const Color warningLight = Color(0xFFFFFBEB);
  static const Color error = Color(0xFFDC2626);
  static const Color errorLight = Color(0xFFFEF2F2);
  static const Color critical = Color(0xFF7C3AED);
  static const Color criticalLight = Color(0xFFF5F3FF);

  // ─── Spacing (8pt grid) ───────────────────────────────────────────────────
  static const double sp4  = 4.0;
  static const double sp8  = 8.0;
  static const double sp12 = 12.0;
  static const double sp16 = 16.0;
  static const double sp20 = 20.0;
  static const double sp24 = 24.0;
  static const double sp32 = 32.0;
  static const double sp48 = 48.0;

  // ─── Radius ───────────────────────────────────────────────────────────────
  static const double radius = 16.0;
  static const double radiusSm = 8.0;
  static const double radiusLg = 24.0;
  static const BorderRadius borderRadius = BorderRadius.all(Radius.circular(radius));
  static const BorderRadius borderRadiusSm = BorderRadius.all(Radius.circular(radiusSm));

  // ─── Light Theme ──────────────────────────────────────────────────────────
  static ThemeData get light {
    final base = ThemeData(
      useMaterial3: true,
      colorSchemeSeed: accent,
      brightness: Brightness.light,
    );

    return base.copyWith(
      scaffoldBackgroundColor: background,
      dividerColor: border,

      // ── Typography ────────────────────────────────────────────────────────
      textTheme: GoogleFonts.interTextTheme(base.textTheme).copyWith(
        displayLarge: GoogleFonts.inter(fontSize: 32, fontWeight: FontWeight.w700, color: textPrimary, letterSpacing: -0.5),
        displayMedium: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.w700, color: textPrimary, letterSpacing: -0.5),
        headlineLarge: GoogleFonts.inter(fontSize: 24, fontWeight: FontWeight.w600, color: textPrimary),
        headlineMedium: GoogleFonts.inter(fontSize: 20, fontWeight: FontWeight.w600, color: textPrimary),
        headlineSmall: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w600, color: textPrimary),
        titleLarge: GoogleFonts.inter(fontSize: 17, fontWeight: FontWeight.w600, color: textPrimary),
        titleMedium: GoogleFonts.inter(fontSize: 15, fontWeight: FontWeight.w500, color: textPrimary),
        titleSmall: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w500, color: textSecondary),
        bodyLarge: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w400, color: textPrimary),
        bodyMedium: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w400, color: textPrimary),
        bodySmall: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w400, color: textSecondary),
        labelLarge: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500, color: textPrimary),
        labelMedium: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500, color: textSecondary),
        labelSmall: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w500, color: textTertiary),
      ),

      // ── AppBar ────────────────────────────────────────────────────────────
      appBarTheme: AppBarTheme(
        backgroundColor: surface,
        foregroundColor: textPrimary,
        elevation: 0,
        scrolledUnderElevation: 1,
        shadowColor: border,
        surfaceTintColor: Colors.transparent,
        titleTextStyle: GoogleFonts.inter(fontSize: 17, fontWeight: FontWeight.w600, color: textPrimary),
        iconTheme: const IconThemeData(color: textPrimary, size: 22),
        toolbarHeight: 56,
        shape: const Border(bottom: BorderSide(color: border, width: 1)),
      ),

      // ── Card ──────────────────────────────────────────────────────────────
      cardTheme: const CardTheme(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: borderRadius,
          side: BorderSide(color: border),
        ),
        margin: EdgeInsets.zero,
      ),

      // ── Navigation Bar ────────────────────────────────────────────────────
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: surface,
        surfaceTintColor: Colors.transparent,
        indicatorColor: accentLight,
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return const IconThemeData(color: accent, size: 22);
          }
          return const IconThemeData(color: textTertiary, size: 22);
        }),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600, color: accent);
          }
          return GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w500, color: textTertiary);
        }),
        elevation: 0,
        shadowColor: border,
        height: 64,
      ),

      // ── FilledButton ──────────────────────────────────────────────────────
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: accent,
          foregroundColor: Colors.white,
          textStyle: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600),
          shape: const RoundedRectangleBorder(borderRadius: borderRadius),
          minimumSize: const Size(double.infinity, 48),
          elevation: 0,
        ),
      ),

      // ── OutlinedButton ────────────────────────────────────────────────────
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPrimary,
          textStyle: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500),
          shape: const RoundedRectangleBorder(borderRadius: borderRadius),
          side: const BorderSide(color: border),
          minimumSize: const Size(double.infinity, 48),
        ),
      ),

      // ── TextButton ────────────────────────────────────────────────────────
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: accent,
          textStyle: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500),
          shape: const RoundedRectangleBorder(borderRadius: borderRadiusSm),
        ),
      ),

      // ── InputDecoration ───────────────────────────────────────────────────
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: sp16, vertical: sp12),
        border: const OutlineInputBorder(
          borderRadius: borderRadius,
          borderSide: BorderSide(color: border),
        ),
        enabledBorder: const OutlineInputBorder(
          borderRadius: borderRadius,
          borderSide: BorderSide(color: border),
        ),
        focusedBorder: const OutlineInputBorder(
          borderRadius: borderRadius,
          borderSide: BorderSide(color: accent, width: 2),
        ),
        errorBorder: const OutlineInputBorder(
          borderRadius: borderRadius,
          borderSide: BorderSide(color: error),
        ),
        hintStyle: GoogleFonts.inter(fontSize: 14, color: textTertiary),
        labelStyle: GoogleFonts.inter(fontSize: 14, color: textSecondary),
      ),

      // ── Chip ──────────────────────────────────────────────────────────────
      chipTheme: ChipThemeData(
        backgroundColor: background,
        selectedColor: accentLight,
        labelStyle: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500),
        shape: const RoundedRectangleBorder(borderRadius: borderRadiusSm, side: BorderSide(color: border)),
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: sp8, vertical: sp4),
      ),

      // ── Dialog ────────────────────────────────────────────────────────────
      dialogTheme: const DialogTheme(
        backgroundColor: surface,
        surfaceTintColor: Colors.transparent,
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(radiusLg))),
      ),

      // ── Bottom Sheet ──────────────────────────────────────────────────────
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: surface,
        surfaceTintColor: Colors.transparent,
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(radiusLg)),
        ),
      ),

      // ── SnackBar ──────────────────────────────────────────────────────────
      snackBarTheme: SnackBarThemeData(
        backgroundColor: textPrimary,
        contentTextStyle: GoogleFonts.inter(fontSize: 14, color: Colors.white),
        actionTextColor: const Color(0xFF93C5FD),
        shape: const RoundedRectangleBorder(borderRadius: borderRadius),
        behavior: SnackBarBehavior.floating,
      ),

      // ── Divider ───────────────────────────────────────────────────────────
      dividerTheme: const DividerThemeData(
        color: border,
        thickness: 1,
        space: 1,
      ),

      // ── FAB ───────────────────────────────────────────────────────────────
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: accent,
        foregroundColor: Colors.white,
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: borderRadius),
      ),

      // ── ListTile ──────────────────────────────────────────────────────────
      listTileTheme: ListTileThemeData(
        contentPadding: const EdgeInsets.symmetric(horizontal: sp16, vertical: sp4),
        titleTextStyle: GoogleFonts.inter(fontSize: 15, fontWeight: FontWeight.w500, color: textPrimary),
        subtitleTextStyle: GoogleFonts.inter(fontSize: 13, color: textSecondary),
      ),
    );
  }
}
